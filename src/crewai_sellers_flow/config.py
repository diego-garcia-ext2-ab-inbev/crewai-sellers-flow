import os


class Config:

    @property
    def BRAZE_API_KEY(self) -> str:
        return os.environ["BRAZE_API_KEY"]
    
    @property
    def SHAREPOINT_CLIENT_ID(self) -> str:
        return os.environ["SHAREPOINT_CLIENT_ID"]
    
    @property
    def SHAREPOINT_CLIENT_SEC(self) -> str:
        return os.environ["SHAREPOINT_CLIENT_SEC"]
       
    @property
    def SHAREPOINT_SITE_URL(self) -> str:
        return os.environ["SHAREPOINT_SITE_URL"]
    
    @property
    def SHAREPOINT_PATH(self) -> str:
        return os.environ["SHAREPOINT_PATH"]

    @property
    def AZURE_API_BASE(self) -> str:
        return os.environ["AZURE_API_BASE"]
    
    @property
    def AZURE_API_KEY(self) -> str:
        return os.environ["AZURE_API_KEY"]
    
    @property
    def MODEL_VERSION(self) -> str:
        return os.environ["MODEL_VERSION"]
    
    @property
    def MODEL(self) -> str:
        return os.environ["MODEL"]

    
config = Config()
