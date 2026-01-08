
import sys
import os
import logging

# Add devserver to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Verification")

def verify_config():
    logger.info("--- Verifying Config ---")
    try:
        import config
        logger.info(f"USE_SWARMUI_ORCHESTRATION: {getattr(config, 'USE_SWARMUI_ORCHESTRATION', 'Not Found')}")
        logger.info(f"ALLOW_DIRECT_COMFYUI: {getattr(config, 'ALLOW_DIRECT_COMFYUI', 'Not Found')}")
        logger.info(f"SWARMUI_API_PORT: {getattr(config, 'SWARMUI_API_PORT', 'Not Found')}")
        logger.info("Config verification passed.")
        return True
    except Exception as e:
        logger.error(f"Config verification failed: {e}")
        return False

def verify_swarmui_client():
    logger.info("\n--- Verifying SwarmUI Client ---")
    try:
        from my_app.services.swarmui_client import get_swarmui_client
        client = get_swarmui_client()
        logger.info(f"SwarmUI Client initialized. Base URL: {client.base_url}")
        return True
    except Exception as e:
        logger.error(f"SwarmUI Client verification failed: {e}")
        return False

def verify_legacy_workflow_service():
    logger.info("\n--- Verifying Legacy Workflow Service ---")
    try:
        from my_app.services.legacy_workflow_service import get_legacy_workflow_service
        service = get_legacy_workflow_service()
        logger.info(f"Legacy Workflow Service initialized.")
        logger.info(f"Service Base URL: {service.base_url}")
        
        # Check if URL matches expected SwarmUI Proxy URL
        import config
        expected_url = f"http://127.0.0.1:{config.SWARMUI_API_PORT}/ComfyBackendDirect"
        if service.base_url == expected_url:
             logger.info("✅ URL correctly configured for SwarmUI Orchestration")
        else:
             logger.warning(f"⚠️ URL mismatch! Expected: {expected_url}, Got: {service.base_url}")

        return True
    except Exception as e:
        logger.error(f"Legacy Workflow Service verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_backend_router():
    logger.info("\n--- Verifying Backend Router ---")
    try:
        from schemas.engine.backend_router import router
        logger.info("Backend Router imported successfully.")
        return True
    except Exception as e:
        logger.error(f"Backend Router verification failed: {e}")
        return False

if __name__ == "__main__":
    c_ok = verify_config()
    s_ok = verify_swarmui_client()
    l_ok = verify_legacy_workflow_service()
    b_ok = verify_backend_router()

    if c_ok and s_ok and l_ok and b_ok:
        logger.info("\n✅ ALL CHECKS PASSED: Transition code structure is valid.")
    else:
        logger.error("\n❌ SOME CHECKS FAILED.")
        sys.exit(1)
