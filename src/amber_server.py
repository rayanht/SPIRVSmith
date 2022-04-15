import json
import platform
import subprocess
from google.cloud import pubsub_v1, storage

AMBER_PATH = "bin/amber"

PLATFORM = platform.system()
VK_ICD_FILENAMES_SWIFTSHADER = (
    "/Users/rayan/swiftshader/build/Darwin/vk_swiftshader_icd.json"
)
VK_ICD_FILENAMES_MOLTENVK = (
    "/Users/rayan/VulkanSDK/1.2.198.1/macOS/share/vulkan/icd.d/MoltenVK_icd.json"
)


STORAGE_CLIENT = storage.Client.from_service_account_json("infra/spirvsmith_gcp.json")
BUCKET = STORAGE_CLIENT.get_bucket("spirv_shaders_bucket")

PROJECT_ID = "spirvsmith"
SUBSCRIPTION_ID = "spirv_shader_pubsub_subscription"
SUBSCRIBER_CLIENT = pubsub_v1.SubscriberClient.from_service_account_json(
    "infra/spirvsmith_gcp.json"
)

SUBSCRIPTION_PATH = SUBSCRIBER_CLIENT.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)


def fetch_amber_file_from_GCS(shader_id: str) -> None:
    blob = BUCKET.blob(f"{shader_id}/out.amber")
    blob.download_to_filename("tmp.amber")


def run_amber():
    # TODO add backend rotation
    process: subprocess.CompletedProcess = subprocess.run(
        [
            AMBER_PATH,
            "-t",
            "spv1.3",
            "-v",
            "1.2",
            f"tmp.amber",
        ],
        capture_output=True,
    )
    if process.stderr:
        print(process.stderr.decode("utf-8"))
    # if process.returncode != 0:
    #     # self.monitor.error(
    #     #     event=Event.AMBER_FAILURE,
    #     #     extra={
    #     #         "stderr": process.stderr.decode("utf-8"),
    #     #         "cli_args": str(process.args),
    #     #         "shader_id": shader.id,
    #     #     },
    #     # )
    # else:
    #     # self.monitor.info(event=Event.AMBER_SUCCESS, extra={"shader_id": shader.id})

    return process.returncode == 0


def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    shader_id: str = json.loads(message.data.decode("utf-8"))["shader_id"]
    fetch_amber_file_from_GCS(shader_id)
    run_amber()
    message.ack()


streaming_pull_future = SUBSCRIBER_CLIENT.subscribe(
    SUBSCRIPTION_PATH, callback=callback
)
print(f"Listening for messages on {SUBSCRIPTION_PATH}..\n")

with SUBSCRIBER_CLIENT:
    streaming_pull_future.result()
