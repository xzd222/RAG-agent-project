try:
    from .config_handler import prompts_config
except ImportError:
    from config_handler import prompts_config

try:
    from .path_tool import get_abs_path
except ImportError:
    from path_tool import get_abs_path
try:
    from .logger_handler import logger
except ImportError:
    from logger_handler import logger


def load_system_prompts():
    try:
        system_prompts_path = get_abs_path(prompts_config["main_prompt_path"])
    except KeyError as k:
        logger.error(f"[load_system_prompts]在yaml中无配置项")
        return k
    
    try:
        return open(system_prompts_path,"r",encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_system_prompts]解析系统提示词出错,{str(e)}")
        return e


def load_rag_prompts():
    try:
        rag_prompts_path = get_abs_path(prompts_config["rag_summarize_prompt_path"])
    except KeyError as k:
        logger.error(f"[load_rag_prompts]在yaml中无配置项")
        return k
    
    try:
        return open(rag_prompts_path,"r",encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_rag_prompts]解析系统提示词出错,{str(e)}")
        return e
    

def load_report_prompts():
    try:
        report_prompts_path = get_abs_path(prompts_config["report_prompt_path"])
    except KeyError as k:
        logger.error(f"[load_report_prompts]在yaml中无配置项")
        return k
    
    try:
        return open(report_prompts_path,"r",encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_report_prompts]解析系统提示词出错,{str(e)}")
        return e
    
if __name__=="__main__":
    print(load_system_prompts())