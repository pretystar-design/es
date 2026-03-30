package main

import (
    "bytes"
    "fmt"
)

// GenerateHCL converts a Project model into a minimal HCL representation.
func GenerateHCL(p Project) (string, error) {
    var buf bytes.Buffer
    // Build a map of dependencies: target ID -> slice of source IDs
    depMap := make(map[string][]string)
    for _, e := range p.Edges {
        // Treat every edge as a depends_on relationship for now
        depMap[e.Target] = append(depMap[e.Target], e.Source)
    }
    for _, n := range p.Nodes {
        fmt.Fprintf(&buf, "resource \"%s\" \"%s\" {\n", n.Type, n.ID)
        for k, v := range n.Attributes {
            fmt.Fprintf(&buf, "  %s = \"%s\"\n", k, v)
        }
        // Add depends_on if present
        if deps, ok := depMap[n.ID]; ok && len(deps) > 0 {
            fmt.Fprint(&buf, "  depends_on = [")
            for i, src := range deps {
                if i > 0 {
                    fmt.Fprint(&buf, ", ")
                }
                fmt.Fprintf(&buf, "\"%s\"", src)
            }
            fmt.Fprintln(&buf, "]")
        }
        fmt.Fprintln(&buf, "}")
        fmt.Fprintln(&buf)
    }
    return buf.String(), nil
}
