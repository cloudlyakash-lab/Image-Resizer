"""
Sharing Service for Android and Desktop environments.
Dispatches native Android ACTION_SEND intent with FileProvider URIs.
"""
import os
from kivy.utils import platform

class SharingService:
    """
    Shares processed images to other applications via Android Intent or system dialog.
    """

    @staticmethod
    def share_image(file_path: str, mime_type: str = "image/*"):
        """Dispatches native share intent."""
        if not os.path.exists(file_path):
            raise FileNotFoundError("Image file does not exist to share.")

        if platform == 'android':
            try:
                from jnius import autoclass, cast
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                File = autoclass('java.io.File')
                FileProvider = autoclass('androidx.core.content.FileProvider')

                currentActivity = PythonActivity.mActivity
                image_file = File(file_path)
                
                # Retrieve package FileProvider URI
                package_name = currentActivity.getPackageName()
                content_uri = FileProvider.getUriForFile(
                    currentActivity,
                    f"{package_name}.fileprovider",
                    image_file
                )

                send_intent = Intent(Intent.ACTION_SEND)
                send_intent.setType(mime_type)
                send_intent.putExtra(Intent.EXTRA_STREAM, content_uri)
                send_intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

                chooser_intent = Intent.createChooser(send_intent, "Share Resized Image")
                currentActivity.startActivity(chooser_intent)
                return True
            except Exception as e:
                print(f"[SharingService] Android native share error: {e}")
                # Fallback to direct URI intent if FileProvider fails
                try:
                    Uri = autoclass('android.net.Uri')
                    uri = Uri.fromFile(File(file_path))
                    send_intent = Intent(Intent.ACTION_SEND)
                    send_intent.setType(mime_type)
                    send_intent.putExtra(Intent.EXTRA_STREAM, uri)
                    currentActivity.startActivity(Intent.createChooser(send_intent, "Share Resized Image"))
                    return True
                except Exception as inner_e:
                    print(f"[SharingService] Fallback share also failed: {inner_e}")
                    return False

        print(f"[SharingService] Sharing on desktop: {file_path}")
        return True
