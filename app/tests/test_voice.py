import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from app.core.podcast.voice import create_audio, delete_source_mp3
from app.core.utilities import (
    AWS_ACCESS_KEY_ID,
    AWS_BUCKET_NAME,
    AWS_REGION_NAME,
    AWS_SECRET_ACCESS_KEY,
    DATA_DIR,
    engine,
    lingo,
    podcast_host,
    today_iso_fmt,
)


class AudioConversionTestCase(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.text_file = os.path.join(self.temp_dir, f"{today_iso_fmt}_content.txt")
        with open(self.text_file, "w") as f:
            f.write("This is some content")

    def tearDown(self):
        # Remove temporary directory and its contents
        shutil.rmtree(self.temp_dir)

    @patch("app.core.podcast.voice.boto3.client")
    @patch("app.core.podcast.voice.pathlib.Path.mkdir")
    def test_create_audio(self, mock_mkdir, mock_boto3_client):
        # Mocking the required dependencies
        mock_polly_client = MagicMock()
        mock_s3_client = MagicMock()
        mock_boto3_client.side_effect = [mock_polly_client, mock_s3_client]

        # Mocking the response from AWS Polly
        mock_polly_client.start_speech_synthesis_task.return_value = {
            "SynthesisTask": {
                "TaskId": "mock_task_id",
                "OutputUri": f"s3://{AWS_BUCKET_NAME}/example/mock_task_id.raw.mp3",
            }
        }

        # Mocking the response from AWS Polly after task completion
        mock_polly_client.get_speech_synthesis_task.return_value = {
            "SynthesisTask": {
                "TaskStatus": "completed",
            }
        }

        # Mocking the download file path
        mock_src_mp3 = f"{DATA_DIR}/{today_iso_fmt}/{today_iso_fmt}.src.mp3"

        # Calling the function under test
        output_key = create_audio(self.text_file)

        # Assertions
        self.assertEqual(output_key, "zed-news/mock_task_id.raw.mp3")
        mock_polly_client.start_speech_synthesis_task.assert_called_once_with(
            Engine=engine,
            LanguageCode=lingo,
            VoiceId=podcast_host,
            Text="This is some content",
            OutputS3BucketName=AWS_BUCKET_NAME,
            OutputS3KeyPrefix=f"zed-news/{today_iso_fmt}-raw",
            OutputFormat="mp3",
        )
        mock_polly_client.get_speech_synthesis_task.assert_called_once_with(TaskId="mock_task_id")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_s3_client.download_file.assert_called_once_with(
            AWS_BUCKET_NAME, "zed-news/mock_task_id.raw.mp3", mock_src_mp3
        )

    @patch("app.core.podcast.voice.boto3.client")
    def test_delete_source_mp3(self, mock_boto3_client):
        # Mocking the required dependencies
        mock_s3_client = MagicMock()
        mock_boto3_client.return_value = mock_s3_client

        # Mocking the output key
        mock_output_key = "example/mock_task_id.raw.mp3"

        # Calling the function under test
        delete_source_mp3(mock_output_key)

        # Assertions
        mock_boto3_client.assert_called_once_with(
            "s3",
            region_name=AWS_REGION_NAME,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        mock_s3_client.delete_object.assert_called_once_with(
            Bucket=AWS_BUCKET_NAME,
            Key="example/mock_task_id.raw.mp3",
        )


if __name__ == "__main__":
    unittest.main()
