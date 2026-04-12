//go:build ignore

package main

import (
	"fmt"
	"net/http"
)

func main() {
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "SERVER WORKING")
	})

	fmt.Println("Server running on 0.0.0.0:8080")

	err := http.ListenAndServe("0.0.0.0:8080", nil)
	if err != nil {
		fmt.Println("Error:", err)
	}
}
