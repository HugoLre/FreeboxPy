# FreeboxPy
A Python3 API for FreeboxV6

## Disclaimer
This API is **VERY INSECURE**. Use it in application that only you can have access to.

## Getting an API token
If you launch FreeboxAPI with no token specified, it will generate and display a token for you. **To avoid duplication of application in the Freebox Server system, you can reuse your token by passing it as an argument when you instantiate the API. See example below.**


## Methods
### get\_active\_ips()
Return array of all the actives ips on the network.



## Example

```python
from freebox_api import FreeboxAPI

free_api = FreeboxAPI("<Your Token Here>")
active_ips = free_api.get_active_ips()
for ip in active_ips:
    print(ip, "is active on the network")
```
