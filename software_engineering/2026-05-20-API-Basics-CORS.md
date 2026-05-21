# qubit-note: APIs | CORS

## Overview

In thiss note we will go over Cross-Origin Resource Sharing or CORS



## Cross-Origin Resource Sharing


Implementing CORS with FastAPI is straightforward:

```
from fastapi. middleware.cors import CORSMiddleware

app.add_middleware(
   CORSMiddleware,
   allow_origins=["*"],
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)
```

where:

- ```allow_origins```: defines which domains can access the API.
- ```allow_methods```: controls allowed HTTP methods.
- ```allow_headers```: allows specific headers.

The above is just indicative. Most of the time you won't want to use the wildcard ```*``` but rather explicitly state the origins the methods and the 
headers your API supports.

CORS configuration is important when connecting frontend applications with backend APIs.



## Summary


## References

