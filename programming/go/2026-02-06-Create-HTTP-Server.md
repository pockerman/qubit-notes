# qubit-note: Go Programming Series | Create an HTTP Server in Go


```
package main
import ("log"
        "net/http"
)


type hello struct{}


func (h hello) ServeHTTP(w http.ResponseWriter, r *http.Request)
{
   msg := "<h1>Hello World</h1>"
   w.Write([]byte(msg))
}



func main()
{
	log.Fatal(htpp.ListenAndServe(":8080", hell{}))
}

```

Open  a terminal, inside your hello-world-server folder, and type in the
following command:

```
go run .
```

Now, open your browser at the following address: http://localhost:8080