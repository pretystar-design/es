package main

type Node struct {
    ID         string            `json:"id"`
    Type       string            `json:"type"`
    Attributes map[string]string `json:"attributes"`
}

type Edge struct {
    Source string `json:"source"`
    Target string `json:"target"`
    Type   string `json:"type"`
}

type Project struct {
    Nodes []Node `json:"nodes"`
    Edges []Edge `json:"edges"`
}
