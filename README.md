# SPIRVSmith

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/rayanht/SPIRVSmith/Build,%20Test%20and%20Deploy)
![GitHub](https://img.shields.io/github/license/rayanht/SPIRVSmith)
[![Test Coverage](https://api.codeclimate.com/v1/badges/5f91595e621ebb1f1da2/test_coverage)](https://codeclimate.com/github/rayanht/SPIRVSmith/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/5f91595e621ebb1f1da2/maintainability)](https://codeclimate.com/github/rayanht/SPIRVSmith/maintainability)
[![FOSSA Status](https://app.fossa.com/api/projects/custom%2B22322%2Fgithub.com%2Frayanht%2FSPIRVSmith.svg?type=shield)](https://app.fossa.com/projects/custom%2B22322%2Fgithub.com%2Frayanht%2FSPIRVSmith?ref=badge_shield)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Introduction

SPIRVSmith is a differential testing tool that leverages structured fuzzing techniques to find bugs in producers and consumers of SPIRV shaders.

SPIRVSmith attempts to find bugs in the following projects:
- [SPIRV-Tools](https://github.com/KhronosGroup/SPIRV-Tools) - mostly the validator and reducer components.
- [SPIRV-Cross](https://github.com/KhronosGroup/SPIRV-Cross)
- [Amber](https://github.com/google/amber)
- [SwiftShader](https://github.com/google/swiftshader)
- [MoltenVK](https://github.com/KhronosGroup/MoltenVK)
- ...and more to come!


## How does it work?

### Differential Testing
The bread and butter of `SPIRVSmith` is **differential testing** (sometimes called differential fuzzing), in which we provide the same SPIRV shader to similar consumers (say three different SPIRV compilers for example), execute the three resulting programs and compare the values contained inside all buffers at the end of exeuction. 

In a **fully deterministic** program `(== synchronous && free of undefined behaviour)`, we expect all these buffers to be exactly the same at the end of execution, regardless of what compiler was used to generate said program. If one program ends up with different buffers than the other two, we have a strong reason to believe that the compiler that generated it has a **bug**.

This concept can be extended further by varying the platform that executes the shader. If we get different results by running the same shader on an Nvidia GPU, an AMD GPU, and an Intel integrated graphics chip then there is a good chance that either the underlying Vulkan engine or the GPU driver has a **bug** (possibly both).

The constraint on determinism creates an interesting problem, how can we ensure that the **randomly** generated programs are free of undefined behaviour? Unlike existing differential testing tools, `SPIRVSmith` does not perform any static analysis or backtracking at generation-time to enforce this constraint, we rather implement the idea of **program reconditioning** by **Donaldson et al.**

### Program Reconditioning

**Donaldson et al.** introduce the idea of program reconditioning as "a method for leveraging off-the-shelf test case reducers to simplify programs that expose miscompilation bugs during randomised differential testing". 

This approach solves the issues raised by **Yang et al.** in the case of [CSmith](https://github.com/csmith-project/csmith) where test case reducers couldn't be used to provide concise, actionable bug reports since they would themselves often introduce undefined behaviour. 

Program reconditioning works by decoupling the process of generating a program and the process of ensuring that said program is free of undefined behaviour. This is in contrast to **Livinskii et al.** in [YARPGen](https://github.com/intel/yarpgen) where code generation steps and static analysis steps are interleaved. 

**Donaldson et al.** describe a **rule-based reconditioning approach** where transforms are applied to constructs that **could** exhibit undefined behaviour. Transforms are applied to all eligible construct in a blanket manner, **no** static analysis is performed to determine which constructs are in fact worth reconditioning. Here is example of reconditioning a **GLSL** shader:

#### Original 
```glsl
float A [3]; // Not initialised
void main () {
    int i = int (A[0]);
    float f = 2000000.0;
    while (i != -42) { // Might not terminate
        A[i] = f; // Out of  bounds ?
        f = f + f; // Roundoff
        int j = i ++ +; // Order of side effects
        ( i / ( i - 1)); // Divide by zero ?
        i = j;
    }
}
```

#### Reconditioned 
```glsl
// [ Declarations of SAFE_ABS , MAKE_IN_RANGE and SAFE_DIV ]
uint _loop_count = 0u;
const uint _loop_limit = 100u;
float A [3] = float [3](1.0 , 1.0 , 1.0);
void main () {
    int i = int (A[0]);
    float f = 2000000.0;
    while (i != -42) {
        if (_loop_count >= _loop_limit) break;
        _loop_count ++;
        A[SAFE_ABS(i) % 3] = f ;
        f = MAKE_IN_RANGE(f + f);
        int _t = SAFE_DIV(i , i - 1);
        int j = i ++ + _t;
        i = j;
    }
}
```

### Architecture

<img width="680" alt="image" src="https://user-images.githubusercontent.com/42040895/162283079-cb762f8f-b018-429c-b187-a4c58b9d19bf.png">

## SPIRV Language Coverage

<details>


<summary>Expand</summary>

### Instructions


#### Miscellanous

<details>


<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpNop | :red_circle: |
| OpUndef | :red_circle: |
| OpSizeOf | :red_circle: |

</details>

#### Debug

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

#### Annotation

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

#### Extension

<details>

<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpExtension | :red_circle: |
| OpExtInstImport | :red_circle: |
| OpExtInst | :red_circle: |

</details>

#### Mode-Setting

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

#### Type-Declaration

<details>

<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpTypeVoid | :white_check_mark: |
| OpTypeBool | :white_check_mark: |
| OpTypeInt | :white_check_mark: |
| OpTypeFloat | :white_check_mark: |
| OpTypeVector | :white_check_mark: |
| OpTypeMatrix | :white_check_mark: |
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

#### Constant-Creation

<details>

<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpConstantTrue | :white_check_mark: |
| OpConstantFalse | :white_check_mark: |
| OpConstant | :white_check_mark: |
| OpConstantComposite | :white_check_mark: |
| OpConstantSampler | :red_circle: |
| OpConstantNull | :red_circle: |
| OpSpecConstantTrue | :red_circle: |
| OpSpecConstantFalse | :red_circle: |
| OpSpecConstant | :red_circle: |
| OpSpecConstantComposite | :red_circle: |
| OpSpecConstantOp | :red_circle: |

</details>

#### Memory

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

#### Function

<details>

<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpFunction | :white_check_mark: |
| OpFunctionParameter | :white_check_mark: |
| OpFunctionEnd | :white_check_mark: |
| OpFunctionCall | :red_circle: |

</details>

#### Image

<details>

<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpSampledImage | :red_circle: |
| OpImageSampleImplicitLod | :red_circle: |
| OpImageSampleExplicitLod | :red_circle: |
| OpImageSampleDrefImplicitLod |:red_circle:  |
| OpImageSampleDrefExplicitLod | :red_circle: |
| OpImageSampleProjImplicitLod | :red_circle: |
| OpImageSampleProjExplicitLod | :red_circle: |
| OpImageSampleProjDrefImplicitLod | :red_circle: |
| OpImageSampleProjDrefExplicitLod | :red_circle: |
| OpImageFetch | :red_circle: |
| OpImageGather | :red_circle: |
| OpImageDrefGather | :red_circle: | 
| OpImageRead | :red_circle: |
| OpImageWrite | :red_circle: |
| OpImage | :red_circle: |
| OpImageQueryFormat | :red_circle: |
| OpImageQueryOrder | :red_circle: |
| OpImageQuerySizeLod | :red_circle: | 
| OpImageQuerySize | :red_circle: |
| OpImageQueryLod | :red_circle: |
| OpImageQueryLevels | :red_circle: |
| OpImageQuerySamples | :red_circle: |
| OpImageSparseSampleImplicitLod | :red_circle: |
| OpImageSparseSampleExplicitLod | :red_circle: | 
| OpImageSparseSampleDrefImplicitLod | :red_circle: |
| OpImageSparseSampleDrefExplicitLod | :red_circle: |
| OpImageSparseFetch | :red_circle: |
| OpImageSparseGather | :red_circle: | 
| OpImageSparseDrefGather | :red_circle: |
| OpImageSparseTexelsResident | :red_circle: |
| OpImageSparseRead | :red_circle: |

</details>

#### Conversion

<details>

<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpConvertFToU | :white_check_mark: |
| OpConvertFToS | :white_check_mark: |
| OpConvertSToF | :white_check_mark: |
| OpConvertUToF |:white_check_mark:  |
| OpUConvert | :red_circle: |
| OpSConvert | :red_circle: |
| OpFConvert | :red_circle: |
| OpQuantizeToF16 | :red_circle: |
| OpConvertPtrToU | :red_circle: |
| OpSatConvertSToU | :red_circle: |
| OpSatConvertUToS | :red_circle: |
| OpConvertUToPtr | :red_circle: | 
| OpPtrCastToGeneric | :red_circle: |
| OpGenericCastToPtr | :red_circle: |
| OpGenericCastToPtrExplicit | :red_circle: |
| OpBitcast | :red_circle: |

</details>

#### Composite

<details>

<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpVectorExtractDynamic | :red_circle: |
| OpVectorInsertDynamic | :red_circle: |
| OpVectorShuffle | :red_circle: |
| OpCompositeConstruct |:red_circle:  |
| OpCompositeExtract | :red_circle: |
| OpCompositeInsert | :red_circle: |
| OpCopyObject | :red_circle: |
| OpTranspose | :red_circle: |
| OpCopyLogical | :red_circle: |

</details>

#### Arithmetic

<details>

<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpSNegate | :white_check_mark: |
| OpFNegate | :white_check_mark: |
| OpIAdd | :white_check_mark: |
| OpFAdd |:white_check_mark:  |
| OpISub | :white_check_mark: |
| OpFSub | :white_check_mark: |
| OpIMul | :white_check_mark: |
| OpFMul | :white_check_mark: |
| OpUDiv | :white_check_mark: |
| OpSDiv | :white_check_mark: |
| OpFDiv | :white_check_mark: |
| OpUMod | :white_check_mark: |
| OpSRem | :white_check_mark: |
| OpSMod | :white_check_mark: |
| OpFRem | :white_check_mark: |
| OpFMod | :white_check_mark: |
| OpVectorTimesScalar | :red_circle: |
| OpMatrixTimesScalar | :red_circle: |
| OpVectorTimesMatrix | :red_circle: |
| OpMatrixTimesVector | :red_circle: |
| OpMatrixTimesMatrix | :red_circle: |
| OpOuterProduct | :red_circle: |
| OpDot | :red_circle: |
| OpIAddCarry | :red_circle: |
| OpISubBorrow | :red_circle: |
| OpUMulExtended | :red_circle: |
| OpSMulExtended | :red_circle: |

</details>

#### Bit

<details>

<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpShiftRightLogical | :white_check_mark: |
| OpShiftRightArithmetic | :white_check_mark: |
| OpShiftLeftLogical | :white_check_mark: |
| OpBitwiseOr |:white_check_mark:  |
| OpBitwiseXor | :white_check_mark: |
| OpBitwiseAnd | :white_check_mark: |
| OpNot | :white_check_mark: |
| OpBitFieldInsert | :red_circle: |
| OpBitFieldSExtract | :red_circle: |
| OpBitFieldUExtract | :red_circle: |
| OpBitReverse | :red_circle: |
| OpBitCount | :white_check_mark: |

</details>

#### Relational and Logical

<details>

<summary>Expand</summary>


|OpCode| Status |
|--|--|
| OpAny | :red_circle: |
| OpAll | :red_circle: |
| OpIsNan | :white_check_mark: |
| OpIsInf |:white_check_mark:  |
| OpIsFinite | :white_check_mark: |
| OpIsNormal | :white_check_mark: |
| OpSignBitSet | :white_check_mark: |
| OpOrdered | :white_check_mark: |
| OpUnordered | :white_check_mark: |
| OpLogicalEqual | :white_check_mark: |
| OpLogicalNotEqual | :white_check_mark: |
| OpLogicalOr | :white_check_mark: |
| OpLogicalAnd | :white_check_mark: |
| OpLogicalNot | :white_check_mark: |
| OpSelect |:white_check_mark:  |
| OpIEqual | :white_check_mark: |
| OpINotEqual | :white_check_mark: |
| OpUGreaterThan | :white_check_mark: |
| OpSGreaterThan | :white_check_mark: |
| OpUGreaterThanEqual | :white_check_mark: |
| OpSGreaterThanEqual | :white_check_mark: |
| OpULessThan | :white_check_mark: |
| OpSLessThan | :white_check_mark: |
| OpULessThanEqual | :white_check_mark: |
| OpSLessThanEqual | :white_check_mark: |
| OpFOrdEqual | :white_check_mark: |
| OpFUnordEqual | :white_check_mark: |
| OpFOrdNotEqual | :white_check_mark: |
| OpFUnordNotEqual | :white_check_mark: |
| OpFOrdLessThan | :white_check_mark: |
| OpFUnordLessThan | :white_check_mark: |
| OpFOrdGreaterThan | :white_check_mark: |
| OpFUnordGreaterThan | :white_check_mark: |
| OpFOrdLessThanEqual | :white_check_mark: |
| OpFUnordLessThanEqual | :white_check_mark: |
| OpFOrdGreaterThanEqual | :white_check_mark: |
| OpFUnordGreaterThanEqual | :white_check_mark: |

</details>

</details>

## License
[![FOSSA Status](https://app.fossa.com/api/projects/custom%2B22322%2Fgithub.com%2Frayanht%2FSPIRVSmith.svg?type=large)](https://app.fossa.com/projects/custom%2B22322%2Fgithub.com%2Frayanht%2FSPIRVSmith?ref=badge_large)
