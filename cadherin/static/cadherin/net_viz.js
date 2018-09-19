var svg = d3.select("svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height");

var color = d3.scaleOrdinal(d3.schemeCategory20);

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function (d) {
        return d.id;
    }))
    .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter(width / 2, height / 2));


d3.csv(nodes_loc, function (error, nodes) {
    //console.log(nodes);
    d3.csv(collabs_loc, function (error, edges) {

        //console.log(edges);

        if (error) throw error;

        var link = svg.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(edges)
            .enter().append("line")
            .attr("stroke-width", 1);

        var node = svg.append("g")
            .attr("class", "nodes")
            .selectAll("g")
            .data(nodes)
            .enter().append("g")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        node.append("text")
            .attr("dy", ".35em")
            .attr("opacity", "0")
            .text(function (d) {
                return d.name;
            });

        var node_disp = node.append("circle")
            .attr("r", 5)
            .attr("fill", function (d) {
                return color(1);
            });

        node_disp.on("mouseover", function () {
            d3.select(this)
                .transition()
                .attr("r", 10)
            d3.select(this.parentNode)
                .select("text")
                .attr("opacity", "1");
        });

        node_disp.on("mouseout", function () {
            d3.select(this)
                .transition()
                .attr("r", 5);
            d3.select(this.parentNode)
                .select("text")
                .attr("opacity", "0");
        });

        node.append("title")
            .text(function (d) {
                return d.name;
            });

        simulation
            .nodes(nodes)
            .on("tick", ticked);

        simulation.force("link")
            .links(edges);

        function ticked() {
            link
                .attr("x1", function (d) {
                    return d.source.x;
                })
                .attr("y1", function (d) {
                    return d.source.y;
                })
                .attr("x2", function (d) {
                    return d.target.x;
                })
                .attr("y2", function (d) {
                    return d.target.y;
                });

            node
                .attr("transform", function (d) {
                    return "translate(" + d.x + "," + d.y + ")";
                });
        }

    });
});


function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}
