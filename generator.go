package main

import (
    "bytes"
    "fmt"
)

// GenerateHCL converts a Project model into a minimal HCL representation.
func GenerateHCL(p Project) (string, error) {
    var buf bytes.Buffer
    for _, n := range p.Nodes {
        fmt.Fprintf(&buf, "resource \"%s\" \"%s\" {\n", n.Type, n.ID)
        for k, v := range n.Attributes {
            fmt.Fprintf(&buf, "  %s = \"%s\"\n", k, v)
        }
        fmt.Fprintln(&buf, "}")
        fmt.Fprintln(&buf)
    }
    // Note: dependencies (edges) are not fully rendered in this minimal example.
    return buf.String(), nil
}
