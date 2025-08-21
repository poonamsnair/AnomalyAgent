import os
from openai import OpenAI, AsyncOpenAI
from typing import Dict, Any, Tuple

from dotenv import load_dotenv
load_dotenv(verbose=True)

from langchain_openai import ChatOpenAI

from src.logger import logger
from src.models.openaillm import OpenAIServerModel
from src.utils import Singleton
from src.proxy.local_proxy import HTTP_CLIENT, ASYNC_HTTP_CLIENT

custom_role_conversions = {"tool-call": "assistant", "tool-response": "user"}
PLACEHOLDER = "PLACEHOLDER"


class ModelManager(metaclass=Singleton):
    def __init__(self):
        self.registed_models: Dict[str, Any] = {}
        
    def init_models(self, use_local_proxy: bool = False):
        self._register_openai_models_simple(use_local_proxy=use_local_proxy)
        self._register_langchain_models_simple(use_local_proxy=use_local_proxy)

    def _check_local_api_key(self, local_api_key_name: str, remote_api_key_name: str) -> str:
        api_key = os.getenv(local_api_key_name, PLACEHOLDER)
        if api_key == PLACEHOLDER:
            logger.warning(f"Local API key {local_api_key_name} is not set, using remote API key {remote_api_key_name}")
            api_key = os.getenv(remote_api_key_name, PLACEHOLDER)
        return api_key
    
    def _check_local_api_base(self, local_api_base_name: str, remote_api_base_name: str) -> str:
        api_base = os.getenv(local_api_base_name, PLACEHOLDER)
        if api_base == PLACEHOLDER:
            logger.warning(f"Local API base {local_api_base_name} is not set, using remote API base {remote_api_base_name}")
            api_base = os.getenv(remote_api_base_name, PLACEHOLDER)
        return api_base
    
    def _register_openai_models_simple(self, use_local_proxy: bool = False):
        """Register essential OpenAI models using unified config"""
        logger.info("Registering OpenAI models with unified configuration")
        
        # Import the unified OpenAI config
        try:
            from configs.config_main import openai_config
            
            # Use environment variable if available, otherwise use config default
            api_key = os.getenv("OPENAI_API_KEY", openai_config.get("api_key", ""))
            api_base = os.getenv("OPENAI_API_BASE", openai_config.get("api_base_url", "https://api.openai.com/v1"))
            
            if not api_key or api_key == PLACEHOLDER:
                logger.warning("No OpenAI API key found - set OPENAI_API_KEY environment variable")
                return
                
            logger.info(f"Using API base: {api_base}")
        except ImportError:
            # Fallback to original method if config not available
            api_key = self._check_local_api_key(local_api_key_name="SKYWORK_API_KEY",
                                                remote_api_key_name="OPENAI_API_KEY")
            api_base = self._check_local_api_base(local_api_base_name="SKYWORK_AZURE_US_API_BASE",
                                                remote_api_base_name="OPENAI_API_BASE")
        
        # Only register essential models
        models_to_register = ["gpt-4o", "gpt-4", "gpt-3.5-turbo"]
        
        for model_name in models_to_register:
            try:
                model = OpenAIServerModel(
                    model_id=model_name,
                    api_base=api_base if api_base != PLACEHOLDER else None,
                    api_key=api_key,
                    custom_role_conversions=custom_role_conversions,
                )
                self.registed_models[model_name] = model
                logger.info(f"✓ Registered OpenAI model: {model_name}")
            except Exception as e:
                logger.warning(f"Failed to register OpenAI model {model_name}: {str(e)}")
    
    def _register_langchain_models_simple(self, use_local_proxy: bool = False):
        """Register essential LangChain models using unified config"""
        logger.info("Registering LangChain models with unified configuration")
        
        # Import the unified OpenAI config
        try:
            from configs.config_main import openai_config
            
            # Use environment variable if available, otherwise use config default
            api_key = os.getenv("OPENAI_API_KEY", openai_config.get("api_key", ""))
            api_base = os.getenv("OPENAI_API_BASE", openai_config.get("api_base_url", "https://api.openai.com/v1"))
            
            if not api_key or api_key == PLACEHOLDER:
                logger.warning("No OpenAI API key found for LangChain models")
                return
        except ImportError:
            # Fallback to original method
            api_key = self._check_local_api_key(local_api_key_name="SKYWORK_API_KEY",
                                                remote_api_key_name="OPENAI_API_KEY")
            api_base = self._check_local_api_base(local_api_base_name="SKYWORK_AZURE_US_API_BASE",
                                                remote_api_base_name="OPENAI_API_BASE")
        
        try:
            # LangChain ChatOpenAI model
            langchain_model = ChatOpenAI(
                model="gpt-4o",
                api_key=api_key,
                base_url=api_base if api_base != PLACEHOLDER else None,
            )
            self.registed_models["langchain-gpt-4o"] = langchain_model
            logger.info("✓ Registered LangChain model: langchain-gpt-4o")
        except Exception as e:
            logger.warning(f"Failed to register LangChain model: {str(e)}")


# Create singleton instance
model_manager = ModelManager()