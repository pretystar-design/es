package main

import (
    "encoding/json"
    "fmt"
    "io/ioutil"
    "os"
)

func main() {
    if len(os.Args) < 2 {
        fmt.Println("Usage: terraform-visual-gen <model.json>")
        os.Exit(1)
    }
    data, err := ioutil.ReadFile(os.Args[1])
    if err != nil {
        fmt.Fprintf(os.Stderr, "error reading file: %v\n", err)
        os.Exit(1)
    }
    var proj Project
    if err := json.Unmarshal(data, &proj); err != nil {
        fmt.Fprintf(os.Stderr, "error parsing JSON: %v\n", err)
        os.Exit(1)
    }
    hcl, err := GenerateHCL(proj)
    if err != nil {
        fmt.Fprintf(os.Stderr, "error generating HCL: %v\n", err)
        os.Exit(1)
    }
    fmt.Println(hcl)
}
