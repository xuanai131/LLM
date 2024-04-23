#!/home/dang/miniconda3/envs/nlp-task/bin/python
import Helper_Utilities
from IPython.display import Image

graph = Helper_Utilities.CreateGraph([])
image = Image(graph.get_graph().draw_png())
with open("graph.png", "wb") as f:
    f.write(graph.get_graph().draw_png())