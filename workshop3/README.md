# Workshop 3 - Wrapping a new tool

> The workshop material and input files are available on the [PMCC-BioinformaticsCore/janis-workshops](https://github.com/PMCC-BioinformaticsCore/janis-workshops) Github page.

## Introduction

A CommandTool is an interface between Janis and a program to be executed. Simply put, a CommandTool has a name, a command, inputs, outputs and a container to run in.

The Janis documentation for [CommandTool](https://janis.readthedocs.io/en/latest/references/commandtool.html) gives an introduction to the tool structure and a template for constructing your own tool.

A tool wrapper must provide all of the information to configure and run the specified tool, this includes the `base_command`, [`janis.ToolInput`](https://janis.readthedocs.io/en/latest/references/commandtool.html#tool-input), [`janis.ToolOutput`](https://janis.readthedocs.io/en/latest/references/commandtool.html#tool-output) and a `container`.

## Requirements

You must have Python 3.6 and Janis installed:

```bash
pip3 install janis-pipelines[bioinformatics,runner]
```

It's recommended you checkout the workshop material:

```bash
git clone https://github.com/PMCC-BioinformaticsCore/janis-workshops.git
```


### Container

> _Further information_: [Dockerizing your tools](https://janis.readthedocs.io/en/latest//tutorials/docker.html)

For portability, we require that you specify an OCI compliant  `container` (eg: Docker) for your tool. Often they're will already be a container with some searching, however here's a guide on [preparing your tools as dockers](https://janis.readthedocs.io/en/latest//tutorials/docker.html) to ensure it works across all environments and workflow specifications.


## Samtools flagstat

In this workshop we're going to wrap `samtools flagstat`. 

### Samtools project links

- Latest version: `1.9`
- Project page: [http://www.htslib.org/doc/samtools.html](http://www.htslib.org/doc/samtools.html)
- Github: [samtools/samtools](https://github.com/samtools/samtools)
- Docker containers: [quay.io/biocontainers/samtools](https://quay.io/repository/biocontainers/samtools?tag=latest&tab=tags) (automatically / community generated)
	- Latest tag: `1.9--h8571acd_11`


### Command tool template

```python
from typing import List, Optional, Union
import janis as j

class ToolName(j.CommandTool):
    @staticmethod
    def tool() -> str:
        return "toolname"
        
    @staticmethod
    def base_command() -> Optional[Union[str, List[str]]]:
        pass

    def inputs(self) -> List[j.ToolInput]:
        return []

    def outputs(self) -> List[j.ToolOutput]:
        return []
        
    @staticmethod
    def container() -> str:
        return ""

    @staticmethod
    def version() -> str:
        pass
```

### Basic information

We can start by filling in the basic information:

- Tool name
- Tool identifier (must be unique within tools)
- Container
- Version

```python
class SamtoolsFlagstat(j.CommandTool):
    @staticmethod
    def tool() -> str:
        return "samtoolsflagstat"

    @staticmethod
    def base_command() -> Optional[Union[str, List[str]]]:
        return ["samtools", "flagstat"]

    # Inputs and outputs
    
    @staticmethod
    def container() -> str:
        return "quay.io/biocontainers/samtools:1.9--h8571acd_11"

    @staticmethod
    def version() -> str:
        return "1.9.0"
```

### Inputs

#### Inspecting inputs with Docker

Although we can check `samtool`'s [documentation], it's often easier to check the help text to find the appropriate tool inputs. We can do that by running the Docker container, and then calling `samtools flagstat` to observe the usage text.

To run the docker container, we can use the following command:

```bash
docker run -it quay.io/biocontainers/samtools:1.9--h8571acd_11
```

To view the help guide, inside our container we can run:

```
# samtools flagstat
```
Output:
```
Usage: samtools flagstat [options] <in.bam>
    --input-fmt-option OPT[=VAL]
            Specify a single input file format option in the form of OPTION or OPTION=VALUE

    -@, --threads INT
            Number of additional threads to use [0]
```


#### Positional Bam input

Our first input we'll focus on is the Bam input. For this we'll need to import the Bam type from `janis.bioinformatics` with the following line:

```python
from janis.bioinformatics.data_types import Bam
```

Our input is required, it has _no prefix_ and we want to place it after our other configuration inputs, so we'll use the following `ToolInput` definition:

```python
j.ToolInput(
	 tag="bam", 
	 input_type=Bam(), 
	 position=1, 
	 doc="Input bam to generate statistics for"
)
```

#### Configuration inputs

Next we'll construct the configuration inputs.

1. `inputFmtOption` is an optional flag (`Boolean`) and has the prefix `--input-fmt-option`, we can use the following `ToolInput` to represent this information:

```python
j.ToolInput("inputFmtOption", j.Boolean(optional=True), prefix="--input-fmt-option", doc="Specify a single input file format option in the form of OPTION or OPTION=VALUE")
```
2. `threads` is an optional integer with the prefix `--threads`:

```python
j.ToolInput("threads", j.Int(optional=True), prefix="--threads", doc="(-@)  Number of additional threads to use [0] ")
```

### Outputs

The only output of `samtools flagstat` is the statistics that are written to `stdout`. We can collect this with the `Stdout` data type. We'll give this the output tag `stats` which will give the following `ToolOutput`:

```python
ToolOutput(tag="stats", output_type=Stdout())
```

### Tool definition

Putting this all together, you should have the following tool definition:

```python
from typing import List, Optional, Union
from janis import CommandTool, ToolArgument, ToolInput, ToolOutput, Stdout, String, Boolean, CpuSelector, Int
from janis.bioinformatics.data_types import Bam

class SamtoolsFlagstat(CommandTool):
    @staticmethod
    def tool() -> str:
        return "samtoolsflagstat"

    @staticmethod
    def base_command() -> Optional[Union[str, List[str]]]:
        return ["samtools", "flagstat"]

    def inputs(self) -> List[ToolInput]:
        return [
            ToolInput("bam", Bam(), position=1, doc="Input bam to generate statistics for"),
            ToolInput("inputFmtOption", Boolean(optional=True), prefix="--input-fmt-option", doc="Specify a single input file format option in the form of OPTION or OPTION=VALUE"),
            ToolInput("threads", Int(optional=True), default=CpuSelector(), prefix="--threads", doc="(-@)  Number of additional threads to use [0] ")
        ]

    def outputs(self) -> List[ToolOutput]:
        return [ToolOutput("out", Stdout())]

    @staticmethod
    def container() -> str:
        return "quay.io/biocontainers/samtools:1.9--h8571acd_11"

    @staticmethod
    def version() -> str:
        return "1.9.0"
```

## Testing the tool

We can test the translation to janis in two different ways:

1. In python:
```python
SamtoolsFlagstat().translate("cwl") # or "wdl"
```

2. Command line
```bash
janis translate samtoolsflagstat.py cwl
```

> If you have multiple command tools or workflows declared in the same file, you can provide a `--name` parameter.

### Running the workflow

We can test the workflow using Janis by first creating an inputs file:

**`inp-job.yml`**
```yaml
bam: /Users/franklinmichael/source/janis-workshops/workshop3/data/brca1.bam
```

Then calling the `janis run` functionality (default CWLTool):

```bash
janis run samtoolsflagstat.py --inputs inp-job.yml
```

OUTPUT:
```
TID:        dc6506
WID:        dc6506
Name:       dc6506

Engine:     cwltool
Engine url: N/A

Path:       /Users/franklinmichael/janis/execution/samtoolsflagstatWf/20190801_121913_dc6506/

Status:     Completed
Duration:   3
Start:      2019-08-01T02:19:13.693171+00:00
Finish:     N/A

Jobs: 

Outputs:    out
2019-08-01T02:19:17+00:00 [INFO]: Hard linking /Users/franklinmichael/janis/execution/samtoolsflagstatWf/20190801_121913_dc6506/workflow/fe348dc8e89f1b03bfdef0b833d222ca8624b359 to /Users/franklinmichael/janis/execution/samtoolsflagstatWf/20190801_121913_dc6506/outputs/out
Finished managing task 'dc6506'. View the task outputs: file:///Users/franklinmichael/janis/execution/samtoolsflagstatWf/20190801_121913_dc6506/
```

We can test this by looking at our output file: 

```bash
cat /Users/franklinmichael/janis/execution/samtoolsflagstatWf/20190801_121913_dc6506/outputs/out
```

## Outcomes

- Learn about the structure of a CommandTool
- Use an existing docker container
- Look at the inputs and outputs of an existing tool
- Globs + InputSelectors






