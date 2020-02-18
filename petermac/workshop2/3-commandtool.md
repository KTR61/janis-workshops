# Workshop 2.3 - Wrapping SamTools Flagstat

## Introduction

A CommandTool is the interface between Janis and a program to be executed. Simply put, a CommandTool has a name, a command, inputs, outputs and a container to run in. Inputs and arguments can have a prefix and / or position, and this is used to construct the command line.

The Janis documentation for the [CommandTool](https://janis.readthedocs.io/en/latest/references/commandtool.html) gives an introduction to the tool structure and a template for constructing your own tool. A tool wrapper must provide all of the information to configure and run the specified tool, this includes the `base_command`, [janis.ToolInput](https://janis.readthedocs.io/en/latest/references/commandtool.html#tool-input), [janis.ToolOutput](https://janis.readthedocs.io/en/latest/references/commandtool.html#tool-output), a `container` and its version.

### Container

> _Further information_: [Containerising your tools](https://janis.readthedocs.io/en/latest/tutorials/container.html)

> Guide on using containers

For portability, Janis requires that you specify an OCI compliant `container` (eg: Docker) for your tool. Often there will already be a container with some searching, however here's a guide on [preparing your tools in containers](https://janis.readthedocs.io/en/latest/tutorials/container.html) to ensure it works across all environments. 


## Samtools flagstat

In this workshop we're going to wrap the `samtools flagstat` tool - flagstat counts the number of alignments for each FLAG type within a bam file.


### Samtools project links

- Latest version: `1.9`
- Project page: [http://www.htslib.org/doc/samtools.html](http://www.htslib.org/doc/samtools.html)
- Github: [samtools/samtools](https://github.com/samtools/samtools)
- Docker containers: [quay.io/biocontainers/samtools](https://quay.io/repository/biocontainers/samtools?tag=latest&tab=tags) (automatically / community generated)
    - Latest tag: `1.9--h8571acd_11`


### Command to build

We want to replicate the following command for `Samtools Flagstat` in Janis:

```bash
samtools flagstat [--threads n] <in.bam>
```

Hence, we can isolate the following information:

- Base commands: `"samtools"`, `"flagstat"`
- The positional `<in.bam>` input
- The configuration `--threads` input


### Command tool template

The following template is the minimum amount of information required to wrap a tool. For more information, see the [CommandToolBuilder documentation](https://janis.readthedocs.io/en/latest/references/commandtool.html).

> We've removed the optional fields: tool_module, tool_provider, metadata, cpu, memory from the following template.

```python
from typing import List, Optional, Union
import janis_core as j

ToolName = j.CommandToolBuilder(
    tool: str="toolname",
    base_command=["base", "command"],
    inputs: List[j.ToolInput]=[],
    outputs: List[j.ToolOutput]=[],
    container="container/name:version",
    version="version"
)
```

### Tool information

Let's start by creating a file with this template inside a second output directory:

```bash
mkdir part2
vim part2/samtoolsflagstat.py
```

We can start by filling in the basic information:

- Rename the variable (ToolName) to be `SamtoolsFlagstat`
- Fill the parameters:
    - `tool`: A unqiue tool identifier, eg: `"SamtoolsFlagStat"`.
    - `base_command` to be `["samtools", "flagstat"]`
    - `container` to be `"quay.io/biocontainers/samtools:1.9--h8571acd_11"`
    - `version` to be `"v1.9.0"`

You'll have a class definition like the following

```python
SamtoolsFlagstat = j.CommandToolBuilder(
    tool: str="samtoolsflagstat",
    base_command=["samtools", "flagstat"],
    container="quay.io/biocontainers/samtools:1.9--h8571acd_11",
    version="1.9.0",
    
    inputs: List[j.ToolInput]=[],
    outputs: List[j.ToolOutput]=[],
)
```

### Inputs


We'll use the [ToolInput](https://janis.readthedocs.io/en/latest/references/commandtool.html#tool-input) class to represent these inputs. A `ToolInput` provides a mechanism for binding this input onto the command line (eg: prefix, position, transformations). See the documentation for more ways to configure a ToolInput.

Our positional input is a Bam, so we'll import the Bam type from `janis` with the following line:

```python
from janis_unix.data_types import TextFile
from janis_bioinformatics.data_types import TextFile, Bam
```

Then we can declare our two inputs:

1. Positional bam input
2. Threads configuration input with the prefix `--threads`

We're going to give our inputs a name through which we can reference them by. This allows us to specify a value from the command line, or connect the result of a previous step [within a workflow](https://janis.readthedocs.io/en/latest/tutorials/tutorial1.html#bwa-mem).

```python
SamtoolsFlagstat = j.CommandToolBuilder(
    # ... tool information
    inputs=[
        # 1. Positional bam input
        j.ToolInput(
            "bam",      # name of our input
            Bam, 
            position=1, 
            doc="Input bam to generate statistics for"
        ),
        # 2. `threads` inputs
        j.ToolInput(
            "threads",  # name of our input
            j.Int(optional=True), 
            prefix="--threads", 
            doc="(-@)  Number of additional threads to use [0] "
        )
    ],
    # outputs
```


### Outputs

We'll use the [ToolOutput](https://janis.readthedocs.io/en/latest/references/commandtool.html#tool-output) class to collect and represent these outputs. A `ToolOutput` has a type, and if not using `stdout` we can provide a `glob` parameter.

The only output of `samtools flagstat` is the statistics that are written to `stdout`. We give this the name `"stats"`, and collect this with the `j.Stdout` data type. We can additionally tell Janis that the Stdout has type [`TextFile`](https://janis.readthedocs.io/en/latest/datatypes/textfile.html).

```python
SamtoolsFlagstat = j.CommandToolBuilder(
    # ... tool information + inputs
    outputs=[
        j.ToolOutput("stats", j.Stdout(TextFile))
    ]
)
```

### Tool definition

Putting this all together, you should have the following tool definition:

```python
from typing import List, Optional, Union
import janis_core as j

from janis_unix.data_types import TextFile
from janis_bioinformatics.data_types import Bam

SamToolsFlagstat_1_9 = j.CommandToolBuilder(
    tool="samtoolsflagstat",
    base_command=["samtools", "flagstat"],
    container="quay.io/biocontainers/samtools:1.9--h8571acd_11",
    version="v1.9.0",
    inputs=[
        # 1. Positional bam input
        j.ToolInput("bam", Bam, position=1),
        # 2. `threads` inputs
        j.ToolInput("threads", j.Int(optional=True), prefix="--threads"),
    ],
    outputs=[j.ToolOutput("stats", j.Stdout(TextFile))],
)
```

## Testing the tool

We can test the translation of this from the CLI:

> If you have multiple command tools or workflows declared in the same file, you will need to provide the `--name` parameter with the name of your tool.

```bash
janis translate part2/samtoolsflagstat.py wdl # or cwl
```

In the following translation, we can see the WDL representation of our tool. In particular, the `command` block gives us an indication of how the command line might look:

```wdl
task samtoolsflagstat {
  input {
    Int? runtime_cpu
    Int? runtime_memory
    File bam
    Int? threads
  }
  command <<<
    samtools flagstat \
      ~{"--threads " + threads} \
      ~{bam}
  >>>
  runtime {
    docker: "quay.io/biocontainers/samtools:1.9--h8571acd_11"
    cpu: if defined(runtime_cpu) then runtime_cpu else 1
    memory: if defined(runtime_memory) then "~{runtime_memory}G" else "4G"
    preemptible: 2
  }
  output {
    File stats = stdout()
  }
}
```



### Running the workflow

We can call the `janis run` functionality (default CWLTool), and use the output of our previous step to test this tool:

```bash
janis run -o part2 part2/samtoolsflagstat.py --bam part1/out.bam
```

OUTPUT:
```
WID:        f9e89f
EngId:      f9e89f
Name:       samtoolsflagstatWf
Engine:     cwltool

Task Dir:   $HOME/part2/
Exec Dir:   $HOME/part2/janis/execution/

Status:     Completed
Duration:   4s
Start:      2019-11-14T04:51:59.744526+00:00
Finish:     2019-11-14T04:52:03.869735+00:00
Updated:    Just now (2019-11-14T04:52:05+00:00)

Jobs: 
    [✓] samtoolsflagstat (N/A)       

Outputs:
    - stats: $HOME/part2/stats.txt
```

Janis (and CWLTool) said the tool executed correctly, let's check the output file: 

```bash
cat part2/stats.txt
```

```
20061 + 0 in total (QC-passed reads + QC-failed reads)
0 + 0 secondary
337 + 0 supplementary
0 + 0 duplicates
19971 + 0 mapped (99.55% : N/A)
19724 + 0 paired in sequencing
9862 + 0 read1
9862 + 0 read2
18606 + 0 properly paired (94.33% : N/A)
19544 + 0 with itself and mate mapped
90 + 0 singletons (0.46% : N/A)
860 + 0 with mate mapped to a different chr
691 + 0 with mate mapped to a different chr (mapQ>=5)
```