dev_msg = {}
dev_msg['start_msg'] = f"""
based on the provided text marked with xml tag <info> located in this message return what the user is asking about
the possible values are:
- feature: the user is asking about a specific DPDK feature or function.
- testpmd: the user is asking about a specific testpmd command or how to use it.
- general_app: the user is asking about general application using DPDK.
- gateway: the user is asking about creating or improving gateway application.

you should only return one of the values above.
"""

def get_dev_msg(tag, msg):
    """
    Returns the developer message.
    """
    return dev_msg[tag] + f"<info>{msg}</info>" 