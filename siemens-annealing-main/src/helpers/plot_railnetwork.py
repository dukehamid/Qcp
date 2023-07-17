import json
import os
import textwrap
import matplotlib.pyplot as plt
import networkx as nx


def wrap_label_name(label, line_length):
    # Wrap label name with line breaks after space or "-"
    return "\n".join(textwrap.wrap(label, line_length, break_long_words=False, break_on_hyphens=True))


def plot_rail_network(json_path):
    # load JSON-data
    with open(json_path) as file:
        data = json.load(file)

    # create graph
    G = nx.Graph()

    # Add Stations
    for station in data['stations']:
        G.add_node(station['id'], name=station['name'], capacity=station['capacity'])  # Add capacity as node attribute

    # add Track Lines
    for track_line in data['track_lines']:
        from_station = track_line['from_station']
        to_station = track_line['to_station']
        distance = track_line['distance']
        G.add_edge(from_station, to_station, distance=distance)

        # Determine positions of stations
    positions = nx.spring_layout(G, seed=40, scale=2, center=(0, 0))

    # Set figure size based on the number of stations
    num_stations = len(G.nodes())
    figure_width = num_stations * 2  # Adjust the multiplier as needed
    plt.figure(figsize=(figure_width, 6))  # Height remains fixed at 6 inches

    # Extract node attributes
    node_labels = nx.get_node_attributes(G, 'name')
    node_capacities = nx.get_node_attributes(G, 'capacity')

    # Determine node sizes based on capacities
    node_sizes = [200 * node_capacities[node_id] for node_id in G.nodes()]

    # plot stations with sizes
    nodes = nx.draw_networkx_nodes(G, positions, node_color='lightblue', node_size=node_sizes)

    # plot track lines
    nx.draw_networkx_edges(G, positions, edge_color='gray')

    # plot Labels
    # Wrap label names with line breaks
    node_labels_wrapped = {node_id: wrap_label_name(label, 20) for node_id, label in node_labels.items()}
    nx.draw_networkx_labels(G, positions, labels=node_labels_wrapped)

    # plot Capacities as labels below the station names
    for node_id, label in node_labels.items():
        capacity = node_capacities[node_id]
        x, y = positions[node_id]
        plt.text(x, y - 0.28, f"       Station Capacity: {capacity}", ha='center', va='center', fontsize=8)

    # plot Track Line Labels
    edge_labels = nx.get_edge_attributes(G, 'distance')
    nx.draw_networkx_edge_labels(G, positions, edge_labels=edge_labels)

    # Add legend
    #plt.text(0.65, -1.8, "Line Capacity = 1", ha='right', va='top', fontsize=8)
    #plt.text(0.65, -2.0, "Platform Capacity = 1", ha='right', va='top', fontsize=8)

    # Save the plot image
    directory = "plots"
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_name = os.path.splitext(os.path.basename(json_path))[0]
    output_path = os.path.join(directory, f"railnetwork_{file_name}.png")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()


def plot_all_railnetworks():
    directory = "timetables"
    for file_name in os.listdir(directory):
        if file_name.endswith("_initial_timetable.json"):
            json_path = os.path.join(directory, file_name)
            plot_rail_network(json_path)

