from enum import Enum

class Send_Cmd(Enum):
    OK = b"#ok"
    ALIVE = "#live?"
    ALWAYS_ON = b"#alwayslive"

class Receive_Cmd(Enum):
    RESPONSE_OK = '#tc'
    RESPONSE_ALIVE = '#alive'
    RESPONSE_ALWAYS_ON = "#alwayslive_ok"
    RESPONSE_ALWAYS_VERSAO = "#bpg2e"
