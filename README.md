# SPIRVSmith
A differential testing tool for SPIRV compilers based on fuzzing techniques


# SPIRV Coverage

## Instructions


### Miscellanous

<details>


<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpNop | :red_circle: |
| OpUndef | :red_circle: |
| OpSizeOf | :red_circle: |

</details>

### Debug

<details>

<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpSourceContinued | :red_circle: |
| OpSource | :red_circle: |
| OpSourceExtension | :red_circle: |
| OpName | :red_circle: |
| OpMemberName | :red_circle: |
| OpString | :red_circle: |
| OpLine | :red_circle: |
| OpNoLine | :red_circle: |
| OpModuleProcessed | :red_circle: | 

</details>

### Annotation

<details>

<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpDecorate | :red_circle: |
| OpMemberDecorate | :red_circle: |
| OpDecorationGroup | :red_circle: |
| OpGroupDecorate | :red_circle: |
| OpGroupMemberDecorate | :red_circle: |
| OpDecorateId | :red_circle: |
| OpDecorateString | :red_circle: |
| OpMemberDecorateString | :red_circle: |

</details>

### Extension

<details>

<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpExtension | :red_circle: |
| OpExtInstImport | :red_circle: |
| OpExtInst | :red_circle: |

</details>

### Mode-Setting

<details>

<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpMemoryModel | :white_check_mark: |
| OpEntryPoint | :white_check_mark: |
| OpExecutionMode | :white_check_mark: |
| OpCapability | :red_circle: |
| OpExecutionModeId | :red_circle: |

</details>

### Type-Declaration

<details>

<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpTypeVoid | :white_check_mark: |
| OpTypeBool | :white_check_mark: |
| OpTypeInt | :white_check_mark: |
| OpTypeFloat | :white_check_mark: |
| OpTypeVector | :white_check_mark: |
| OpTypeMatrix | :red_circle: |
| OpTypeImage | :red_circle: |
| OpTypeSampler | :red_circle: |
| OpTypeSampledImage | :red_circle: |
| OpTypeArray | :white_check_mark: |
| OpTypeRuntimeArray | :red_circle: |
| OpTypeStruct | :white_check_mark: |
| OpTypeOpaque | :red_circle: |
| OpTypePointer | :white_check_mark: |
| OpTypeFunction | :white_check_mark: |

</details>

### Constant-Creation

<details>

<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpConstantTrue | :white_check_mark: |
| OpConstantFalse | :white_check_mark: |
| OpConstant | :white_check_mark: |
| OpConstantComposite | :red_circle: |
| OpConstantSampler | :red_circle: |
| OpConstantNull | :red_circle: |
| OpSpecConstantTrue | :red_circle: |
| OpSpecConstantFalse | :red_circle: |
| OpSpecConstant | :red_circle: |
| OpSpecConstantComposite | :red_circle: |
| OpSpecConstantOp | :red_circle: |

</details>

### Memory

<details>

<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpVariable | :white_check_mark: |
| OpImageTexelPointer | :red_circle: |
| OpLoad | :white_check_mark: |
| OpStore |:white_check_mark:  |
| OpCopyMemory | :red_circle: |
| OpCopyMemorySized | :red_circle: |
| OpAccessChain | :red_circle: |
| OpInBoundsAccessChain | :red_circle: |
| OpPtrAccessChain | :red_circle: |
| OpPtrEqual | :red_circle: |
| OpPtrNotEqual | :red_circle: |
| OpPtrDiff | :red_circle: | 

</details>

### Function

<details>

<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpFunction | :white_check_mark: |
| OpFunctionParameter | :white_check_mark: |
| OpFunctionEnd | :white_check_mark: |
| OpFunctionCall | :red_circle: |

</details>
