PlantUML diagram for Experiment 2 (Agent)

Files:
- `diagram_experiment2.puml`: PlantUML source for the compact module-level overview used in Experiment 2.

How to render locally (Windows PowerShell):

1) Using PlantUML jar (requires Java and Graphviz installed):

```powershell
# render PNG at smaller scale for PPT
java -jar path\to\plantuml.jar -tpng -scale 0.7 docs\diagram_experiment2.puml

# or force output width (800px) for slide-friendly image
java -jar path\to\plantuml.jar -tpng -width 800 docs\diagram_experiment2.puml
```

2) Using Docker image (no local Java/Graphviz):

```powershell
docker run --rm -v ${PWD}:/workspace plantuml/plantuml -tpng -scale 0.7 /workspace/docs/diagram_experiment2.puml
```

3) Quick online preview: copy the contents of `diagram_experiment2.puml` and paste into https://www.plantuml.com/plantuml/ or use an online PlantUML editor.

Tips for PowerPoint:
- Render PNG with width ~800px for a single-slide small diagram; increase to 1200px if text becomes too small.
- Use `-scale 0.6` / `-scale 0.7` to shrink output while preserving layout.
- If text looks small, increase width or bump `defaultFontSize` in the `.puml` to 12 and re-render.

Notes:
- This diagram is a compact module-level overview (no method lists) to fit on slides.
- If you want a denser diagram (show method names) I can create a second `.puml` sized for a two-column slide or split into multiple diagrams.
PlantUML diagram for Experiment 2 (Agent)

Files:
- `diagram_experiment2.puml`: PlantUML source for the high-level class/module overview used in Experiment 2.

How to render locally (Windows PowerShell):

1) Using PlantUML jar (requires Java and Graphviz installed):

```powershell
# render PNG
java -jar path\to\plantuml.jar -tpng docs\diagram_experiment2.puml
# render SVG
java -jar path\to\plantuml.jar -tsvg docs\diagram_experiment2.puml
```

2) Using Docker image (no local Java/Graphviz):

```powershell
docker run --rm -v ${PWD}:/workspace plantuml/plantuml -tpng /workspace/docs/diagram_experiment2.puml
```

3) Quick online preview: copy the contents of `diagram_experiment2.puml` and paste into https://www.plantuml.com/plantuml/ or use an online PlantUML editor.

Notes:
- This diagram is an inferred high-level view from the `agent/` code. It represents modules as classes and shows "uses" and instantiation relationships where clear from the code.
- If you want a more detailed diagram (with specific methods/attributes expanded or additional modules included), tell me which files or classes to expand and I'll update the `.puml`.
