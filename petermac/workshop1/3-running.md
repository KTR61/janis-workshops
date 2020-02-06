# Workshop 1.3 - Running workflows with Janis

Let's run the following command to see how to configure Janis when running a workflow:

```
$ janis run -h

usage: janis run [-h] [-i INPUTS] [-o OUTPUT_DIR] [-B] 
                 [--keep-intermediate-files] [...OTHER OPTIONS]
                 workflow [...WORKFLOW INPUTS]
```

> It's important that these configuration options come AFTER the `run`, but before the `<workflow>` argument. Any parameters after the `<workflow>` are passed as inputs to the workflow.

We'll highlight a few options:

- `-o OUTPUT_DIR, --output-dir OUTPUT_DIR` - [REQUIRED] This directory to copy outputs to. By default intermediate results are within a janis/execution subfolder (unless overriden by your configuration)

- `-i INPUTS, --inputs INPUTS` - YAML or JSON inputs file to provide values for the workflow (can specify multiple times)

- `-B, --background` - Run the workflow engine in the background (or submit to a cluster if your template supports it)

- `--keep-intermediate-files` - Do not remove execution directory on successful complete


## Running a test workflow

To test that Janis is configured properly, We'll run a simple workflow called [`Hello`](https://janis.readthedocs.io/en/latest/tools/unix/hello.html) [click the link to see the dcoumentation]. This workflow prints `"Hello, World"` to stdout, and this stdout is captured as an output. This will test that Janis can submit to the cluster correctly.

> We must specify an output directory (`-o`) to contain the execution and outputs, we'll ask Janis to create a subdirectory called `part1` within our `workshop1` directory:

```
janis run -o part1 hello
```

This command will:

- Create an output directory called `part1` (relative to the current directory),
- Start Cromwell,
- Submit to the cluster and run a task that calls "echo",
- Collect the results.


You'll see logs from Cromwell in the terminal. There's a number of statements that are worth highlighting:

```
# 1. Your Workflow ID
[INFO]: Starting task with id = 'c83484'

# 2. The process ID of cromwell (in case of an intermittent failure)
Cromwell is starting with pid=14497

# 3. Cromwell started successfully running the job.
2020-01-31T12:58:46 [INFO]: Status changed to: Running

# 4. The task has completed successfully 
2020-01-31T12:59:05 [INFO]: View the task outputs: file://$HOME/janis-workshop1/part1
```

In our output folder, there are two items (`ls part1`):
```
drwxr-sr-x 8 mfranklin punim0755 133K Jan 31 12:59 janis
-rw-r--r-- 1 mfranklin punim0755   14 Jan 31 12:58 out
```

The output to the task is called `out`, as this is the name of the output that the `hello` tool specifies. The `janis` folder contains information about the execution, including logs.


### Running in the background

We've run the workflow within our terminal session. But often our workflow is too long to run in one session and it would be useful to submit the workflow to the cluster.

The Peter Mac configuration can submit to the janis partition on the cluster when the `--background` (`-B`) parameter is provided. 

The tool [`Hello`](https://janis.readthedocs.io/en/latest/tools/unix/hello.html) allows us to override the default text to print by passing a value for the input `inp`. We can do this by appending `--inp "Hello $(whoami)"`, 

Let's run the same workflow with a new output directory (`part2`), except now providing the background parameter and the new text to print. Janis quickly returns with our workflow ID, which we can capture by running:

```
wid=$(janis run --background -o part2 hello --inp "Hello $(whoami)")
```

We can track the progress of our workflow with:

```
janis watch $wid
```

You will see a progress screen like the following 

```
WID:        d12763
EngId:      291b6f91-6246-4ded-934b-98773e265ead
Name:       hello
Engine:     cromwell (localhost:53489) [PID=43580]

Task Dir:   /Users/franklinmichael/source/CWLab/test2
Exec Dir:   /Users/franklinmichael/source/CWLab/test2/janis/execution/hello/291b6f91-6246-4ded-934b-98773e265ead

Status:     Completed
Duration:   44s
Start:      2020-01-31T02:49:35.968005+00:00
Finish:     2020-01-31T02:50:20.305000+00:00
Updated:    Just now (2020-01-31T02:50:28+00:00)

Jobs: 
    [✓] hello (11s)       

Outputs:
    - out: /Users/franklinmichael/source/CWLab/test2/out
```