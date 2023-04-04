# Memory

Warpspeed supports different types of memory for pipelines. Due to the non-linear nature of workflows you can't use memory with them yet, but we are currently investigating other possibilities.

By default, pipelines don't initialize memory, so you have to explicitly pass it to them:

```python
Pipeline(
    memory=PipelineMemory()
)
```

There are two other types of memory: `BufferPipelineMemory` and `SummaryPipelineMemory`. `BufferPipelineMemory` will keep a sliding window of steps that are used to construct a prompt:

```python
Pipeline(
    memory=BufferPipelineMemory(buffer_size=3)
)
```

This works great for shorter pipelines but fails if the whole workflow context needs to be present. You can use `SummaryMemory` to address that:

```python
Pipeline(
    memory=SummaryPipelineMemory(
        summarizer=PromptDriverSummarizer(
            driver=OpenAiPromptDriver()
        ),
        offset=2
    )
)
```

This will progressively summarize the whole pipeline except for the last two steps.

Finally, you can persist memory by using memory drivers. Warpspeed comes with one memory driver for automatically storing memory in a file on the disk. Here is how you can initialize memory with a driver:

```python
PipelineMemory(
    driver=DiskMemoryDriver(file_path="memory.json")
)
```

To load memory:

```python
DiskMemoryDriver(file_path="memory.json").load()
```

You can easily build drivers for your own data stores by extending `MemoryDriver`. You only need to implement `store` and `load` methods.