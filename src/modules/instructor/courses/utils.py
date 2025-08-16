import httpx
import asyncio
from typing import Tuple
from fastapi import UploadFile
from src.configs.settings import settings
from src.errors.app_errors import AppError
from src.errors.error_codes import ErrorCodes


class MuxUtils:
    """Utility class for handling Mux video operations"""

    def __init__(self):
        self.base_url = "https://api.mux.com/video/v1"
        self.auth = (settings.mux_token_id, settings.mux_token_secret)

    async def create_upload_url(self) -> Tuple[str, str]:
        """
        Step 1: Create a Mux Direct Upload URL
        
        Returns:
            Tuple[str, str]: (upload_url, upload_id)
        """
        create_asset_request = {
            "timeout": 3600,
            "cors_origin": "*",
            "new_asset_settings": {
                "playback_policy": ["public"],
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self.base_url}/uploads",
                                             json=create_asset_request,
                                             auth=self.auth)
                response.raise_for_status()

                upload_data = response.json()["data"]
                upload_url = upload_data["url"]
                upload_id = upload_data["id"]

                return upload_url, upload_id

        except httpx.HTTPStatusError as e:
            error_details = await e.response.aread() if hasattr(
                e.response, 'aread') else e.response.text
            raise AppError(
                ErrorCodes.EXTERNAL_SERVICE_ERROR,
                f"Failed to create Mux upload URL: {e.response.status_code} - {error_details}"
            )
        except Exception as e:
            raise AppError(ErrorCodes.INTERNAL_SERVER_ERROR,
                           f"Unexpected error creating upload URL: {str(e)}")

    async def upload_video_to_mux(self, upload_url: str,
                                  video: UploadFile) -> None:
        """
        Step 2: Upload the video file to the Mux URL
        
        Args:
            upload_url (str): The upload URL from Mux
            video (UploadFile): The video file to upload
        """
        try:
            # Read video content
            video_content = await video.read()

            # Reset file pointer after reading
            await video.seek(0)

            async with httpx.AsyncClient(
                    timeout=300.0) as client:  # Longer timeout for file upload
                upload_response = await client.put(
                    upload_url,
                    content=video_content,
                    headers={'Content-Type': video.content_type})
                upload_response.raise_for_status()

        except httpx.HTTPStatusError as e:
            error_details = await e.response.aread() if hasattr(
                e.response, 'aread') else e.response.text
            raise AppError(
                ErrorCodes.EXTERNAL_SERVICE_ERROR,
                f"Failed to upload video to Mux: {e.response.status_code} - {error_details}"
            )
        except Exception as e:
            raise AppError(ErrorCodes.INTERNAL_SERVER_ERROR,
                           f"Unexpected error uploading video: {str(e)}")

    async def wait_for_asset_processing(self,
                                        upload_id: str,
                                        max_attempts: int = 60
                                        ) -> Tuple[str, float]:
        """
        Step 3: Wait for Mux to process the asset and get asset details
        
        Args:
            upload_id (str): The upload ID from Mux
            max_attempts (int): Maximum polling attempts (default: 60)
            
        Returns:
            Tuple[str, float]: (asset_id, duration)
        """
        asset_id = None
        duration = None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                for attempt in range(max_attempts):
                    await asyncio.sleep(5)  # Wait 5 seconds between checks

                    try:
                        # Check upload status
                        get_upload_response = await client.get(
                            f"{self.base_url}/uploads/{upload_id}",
                            auth=self.auth)
                        get_upload_response.raise_for_status()
                        upload_status = get_upload_response.json()["data"]

                        # Check if asset was created
                        if (upload_status.get("status") == "asset_created"
                                and upload_status.get("asset_id")):

                            asset_id = upload_status["asset_id"]

                            # Get asset details for duration and status
                            get_asset_response = await client.get(
                                f"{self.base_url}/assets/{asset_id}",
                                auth=self.auth)
                            get_asset_response.raise_for_status()
                            asset_data = get_asset_response.json()["data"]

                            # Check if asset is ready
                            if asset_data.get("status") == "ready":
                                duration = asset_data.get("duration", 0.0)
                                break

                    except httpx.HTTPStatusError as e:
                        if attempt == max_attempts - 1:  # Last attempt
                            raise e
                        continue  # Retry on API errors

                if not asset_id:
                    raise AppError(ErrorCodes.INTERNAL_SERVER_ERROR,
                                   "Mux asset processing timed out.")

                if not duration:
                    raise AppError(
                        ErrorCodes.INTERNAL_SERVER_ERROR,
                        "Mux asset processing completed but could not retrieve duration."
                    )

                return asset_id, duration

        except httpx.HTTPStatusError as e:
            error_details = await e.response.aread() if hasattr(
                e.response, 'aread') else e.response.text
            raise AppError(
                ErrorCodes.EXTERNAL_SERVICE_ERROR,
                f"Failed to get asset status from Mux: {e.response.status_code} - {error_details}"
            )
        except AppError:
            raise  # Re-raise AppErrors as-is
        except Exception as e:
            raise AppError(
                ErrorCodes.INTERNAL_SERVER_ERROR,
                f"Unexpected error waiting for asset processing: {str(e)}")

    async def get_asset_playback_id(self, asset_id: str) -> str:
        """
        Get the playback ID for a Mux asset
        
        Args:
            asset_id (str): The Mux asset ID
            
        Returns:
            str: The playback ID for streaming
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/assets/{asset_id}", auth=self.auth)
                response.raise_for_status()

                asset_data = response.json()["data"]
                playback_ids = asset_data.get("playback_ids", [])

                if not playback_ids:
                    raise AppError(ErrorCodes.INTERNAL_SERVER_ERROR,
                                   "No playback IDs found for asset")

                return playback_ids[0]["id"]

        except httpx.HTTPStatusError as e:
            error_details = await e.response.aread() if hasattr(
                e.response, 'aread') else e.response.text
            raise AppError(
                ErrorCodes.EXTERNAL_SERVICE_ERROR,
                f"Failed to get playback ID: {e.response.status_code} - {error_details}"
            )
        except Exception as e:
            raise AppError(ErrorCodes.INTERNAL_SERVER_ERROR,
                           f"Unexpected error getting playback ID: {str(e)}")
