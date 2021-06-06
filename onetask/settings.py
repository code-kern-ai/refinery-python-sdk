# -*- coding: utf-8 -*-
import os

BASE_DIR = "onetask"
BASE_URL = "https://app.dev.onetask.ai"

# files
SIGNATURE_FILE = os.path.join(BASE_DIR, "sdk.signature")

# namespaces
API_NAMESPACE = "api"
SDK_NAMESPACE = "sdk"

# project
PROJECT_INFO_URL = f"{BASE_URL}/{API_NAMESPACE}/{SDK_NAMESPACE}/project_information"

# labeling function
LF_INSTANCE_URL = f"{BASE_URL}/{API_NAMESPACE}/{SDK_NAMESPACE}/lf_instance"
LF_LIST_URL = f"{BASE_URL}/{API_NAMESPACE}/{SDK_NAMESPACE}/lf_list"

# record
RECORD_INSTANCE_URL = f"{BASE_URL}/{API_NAMESPACE}/{SDK_NAMESPACE}/record_instance"
RECORD_LIST_URL = f"{BASE_URL}/{API_NAMESPACE}/{SDK_NAMESPACE}/record_list"
