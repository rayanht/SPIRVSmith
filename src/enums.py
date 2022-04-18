from enum import Enum


class SPIRVEnum(Enum):
    def __str__(self) -> str:
        """

        Returns the SPIRV-legal string
        corresponding to a given enum value.

        Returns:
            str: The SPIRV-legal string corresponding to the enum value.
        """
        return "None" if self.name == "NONE" else self.name


class SourceLanguage(SPIRVEnum):
    Unknown = 0
    ESSL = 1
    GLSL = 2
    OpenCL_C = 3
    OpenCL_CPP = 4
    HLSL = 5
    CPP_for_OpenCL = 6


class ExecutionModel(SPIRVEnum):
    # Vertex = 0
    # TessellationControl = 1
    # TessellationEvaluation = 2
    # Geometry = 3
    Fragment = 4
    GLCompute = 5
    Kernel = 6
    # TaskNV = 5267
    # MeshNV = 5268
    # RayGenerationKHR = 5313
    # RayGenerationNV = 5313
    # IntersectionKHR = 5314
    # IntersectionNV = 5314
    # AnyHitKHR = 5315
    # AnyHitNV = 5315
    # ClosestHitKHR = 5316
    # ClosestHitNV = 5316
    # MissKHR = 5317
    # MissNV = 5317
    # CallableKHR = 5318
    # CallableNV = 5318


class AddressingModel(SPIRVEnum):
    Logical = 0
    Physical32 = 1
    Physical64 = 2
    PhysicalStorageBuffer64 = 5348
    PhysicalStorageBuffer64EXT = 5348


class MemoryModel(SPIRVEnum):
    Simple = 0
    GLSL450 = 1
    OpenCL = 2
    Vulkan = 3
    VulkanKHR = 3


class ExecutionMode(SPIRVEnum):
    Invocations = 0
    SpacingEqual = 1
    SpacingFractionalEven = 2
    SpacingFractionalOdd = 3
    VertexOrderCw = 4
    VertexOrderCcw = 5
    PixelCenterInteger = 6
    OriginUpperLeft = 7
    OriginLowerLeft = 8
    EarlyFragmentTests = 9
    PointMode = 10
    Xfb = 11
    DepthReplacing = 12
    DepthGreater = 14
    DepthLess = 15
    DepthUnchanged = 16
    LocalSize = 17
    LocalSizeHint = 18
    InputPoints = 19
    InputLines = 20
    InputLinesAdjacency = 21
    Triangles = 22
    InputTrianglesAdjacency = 23
    Quads = 24
    Isolines = 25
    OutputVertices = 26
    OutputPoints = 27
    OutputLineStrip = 28
    OutputTriangleStrip = 29
    VecTypeHint = 30
    ContractionOff = 31
    Initializer = 33
    Finalizer = 34
    SubgroupSize = 35
    SubgroupsPerWorkgroup = 36
    SubgroupsPerWorkgroupId = 37
    LocalSizeId = 38
    LocalSizeHintId = 39
    # SubgroupUniformControlFlowKHR = 4421
    # PostDepthCoverage = 4446
    # DenormPreserve = 4459
    # DenormFlushToZero = 4460
    # SignedZeroInfNanPreserve = 4461
    # RoundingModeRTE = 4462
    # RoundingModeRTZ = 4463
    # StencilRefReplacingEXT = 5027
    # OutputLinesNV = 5269
    # OutputPrimitivesNV = 5270
    # DerivativeGroupQuadsNV = 5289
    # DerivativeGroupLinearNV = 5290
    # OutputTrianglesNV = 5298
    # PixelInterlockOrderedEXT = 5366
    # PixelInterlockUnorderedEXT = 5367
    # SampleInterlockOrderedEXT = 5368
    # SampleInterlockUnorderedEXT = 5369
    # ShadingRateInterlockOrderedEXT = 5370
    # ShadingRateInterlockUnorderedEXT = 5371
    # SharedLocalMemorySizeINTEL = 5618
    # RoundingModeRTPINTEL = 5620
    # RoundingModeRTNINTEL = 5621
    # FloatingPointModeALTINTEL = 5622
    # FloatingPointModeIEEEINTEL = 5623
    # MaxWorkgroupSizeINTEL = 5893
    # MaxWorkDimINTEL = 5894
    # NoGlobalOffsetINTEL = 5895
    # NumSIMDWorkitemsINTEL = 5896
    # SchedulerTargetFmaxMhzINTEL = 5903


class StorageClass(SPIRVEnum):
    UniformConstant = 0
    Input = 1
    Uniform = 2
    Output = 3
    # Workgroup = 4
    # CrossWorkgroup = 5
    # Private = 6
    Function = 7
    # Generic = 8
    # PushConstant = 9
    # AtomicCounter = 10
    # Image = 11
    StorageBuffer = 12
    # CallableDataKHR = 5328
    # CallableDataNV = 5328
    # IncomingCallableDataKHR = 5329
    # IncomingCallableDataNV = 5329
    # RayPayloadKHR = 5338
    # RayPayloadNV = 5338
    # HitAttributeKHR = 5339
    # HitAttributeNV = 5339
    # IncomingRayPayloadKHR = 5342
    # IncomingRayPayloadNV = 5342
    # ShaderRecordBufferKHR = 5343
    # ShaderRecordBufferNV = 5343
    # PhysicalStorageBuffer = 5349
    # PhysicalStorageBufferEXT = 5349
    # CodeSectionINTEL = 5605
    # DeviceOnlyINTEL = 5936
    # HostOnlyINTEL = 5937


class Dim(SPIRVEnum):
    Dim1D = 0
    Dim2D = 1
    Dim3D = 2
    Cube = 3
    Rect = 4
    Buffer = 5
    SubpassData = 6


class SamplerAddressingMode(SPIRVEnum):
    NONE = 0
    ClampToEdge = 1
    Clamp = 2
    Repeat = 3
    RepeatMirrored = 4


class SamplerFilterMode(SPIRVEnum):
    Nearest = 0
    Linear = 1


class ImageFormat(SPIRVEnum):
    Unknown = 0
    Rgba32f = 1
    Rgba16f = 2
    R32f = 3
    Rgba8 = 4
    Rgba8Snorm = 5
    Rg32f = 6
    Rg16f = 7
    R11fG11fB10f = 8
    R16f = 9
    Rgba16 = 10
    Rgb10A2 = 11
    Rg16 = 12
    Rg8 = 13
    R16 = 14
    R8 = 15
    Rgba16Snorm = 16
    Rg16Snorm = 17
    Rg8Snorm = 18
    R16Snorm = 19
    R8Snorm = 20
    Rgba32i = 21
    Rgba16i = 22
    Rgba8i = 23
    R32i = 24
    Rg32i = 25
    Rg16i = 26
    Rg8i = 27
    R16i = 28
    R8i = 29
    Rgba32ui = 30
    Rgba16ui = 31
    Rgba8ui = 32
    R32ui = 33
    Rgb10a2ui = 34
    Rg32ui = 35
    Rg16ui = 36
    Rg8ui = 37
    R16ui = 38
    R8ui = 39
    R64ui = 40
    R64i = 41


class ImageChannelOrder(SPIRVEnum):
    R = 0
    A = 1
    RG = 2
    RA = 3
    RGB = 4
    RGBA = 5
    BGRA = 6
    ARGB = 7
    Intensity = 8
    Luminance = 9
    Rx = 10
    RGx = 11
    RGBx = 12
    Depth = 13
    DepthStencil = 14
    sRGB = 15
    sRGBx = 16
    sRGBA = 17
    sBGRA = 18
    ABGR = 19


class ImageChannelDataType(SPIRVEnum):
    SnormInt8 = 0
    SnormInt16 = 1
    UnormInt8 = 2
    UnormInt16 = 3
    UnormShort565 = 4
    UnormShort555 = 5
    UnormInt101010 = 6
    SignedInt8 = 7
    SignedInt16 = 8
    SignedInt32 = 9
    UnsignedInt8 = 10
    UnsignedInt16 = 11
    UnsignedInt32 = 12
    HalfFloat = 13
    Float = 14
    UnormInt24 = 15
    UnormInt101010_2 = 16


class ImageOperandsShift(SPIRVEnum):
    Bias = 0
    Lod = 1
    Grad = 2
    ConstOffset = 3
    Offset = 4
    ConstOffsets = 5
    Sample = 6
    MinLod = 7
    MakeTexelAvailable = 8
    MakeTexelAvailableKHR = 8
    MakeTexelVisible = 9
    MakeTexelVisibleKHR = 9
    NonPrivateTexel = 10
    NonPrivateTexelKHR = 10
    VolatileTexel = 11
    VolatileTexelKHR = 11
    SignExtend = 12
    ZeroExtend = 13
    Nontemporal = 14
    Offsets = 16


class ImageOperandsMask(SPIRVEnum):
    MaskNone = 0
    Bias = 1
    Lod = 2
    Grad = 4
    ConstOffset = 8
    Offset = 16
    ConstOffsets = 32
    Sample = 64
    MinLod = 128
    MakeTexelAvailable = 256
    MakeTexelAvailableKHR = 256
    MakeTexelVisible = 512
    MakeTexelVisibleKHR = 512
    NonPrivateTexel = 1024
    NonPrivateTexelKHR = 1024
    VolatileTexel = 2048
    VolatileTexelKHR = 2048
    SignExtend = 4096
    ZeroExtend = 8192
    Nontemporal = 16384
    Offsets = 65536


class FPFastMathModeShift(SPIRVEnum):
    NotNaN = 0
    NotInf = 1
    NSZ = 2
    AllowRecip = 3
    Fast = 4
    AllowContractFastINTEL = 16
    AllowReassocINTEL = 17


class FPFastMathModeMask(SPIRVEnum):
    MaskNone = 0
    NotNaN = 1
    NotInf = 2
    NSZ = 4
    AllowRecip = 8
    Fast = 16
    AllowContractFastINTEL = 65536
    AllowReassocINTEL = 131072


class FPRoundingMode(SPIRVEnum):
    RTE = 0
    RTZ = 1
    RTP = 2
    RTN = 3


class LinkageType(SPIRVEnum):
    Export = 0
    Import = 1
    LinkOnceODR = 2


class AccessQualifier(SPIRVEnum):
    ReadOnly = 0
    WriteOnly = 1
    ReadWrite = 2


class FunctionParameterAttribute(SPIRVEnum):
    Zext = 0
    Sext = 1
    ByVal = 2
    Sret = 3
    NoAlias = 4
    NoCapture = 5
    NoWrite = 6
    NoReadWrite = 7


class Decoration(SPIRVEnum):
    RelaxedPrecision = 0
    SpecId = 1
    Block = 2
    BufferBlock = 3
    RowMajor = 4
    ColMajor = 5
    ArrayStride = 6
    MatrixStride = 7
    GLSLShared = 8
    GLSLPacked = 9
    CPacked = 10
    BuiltIn = 11
    NoPerspective = 13
    Flat = 14
    Patch = 15
    Centroid = 16
    Sample = 17
    Invariant = 18
    Restrict = 19
    Aliased = 20
    Volatile = 21
    Constant = 22
    Coherent = 23
    NonWritable = 24
    NonReadable = 25
    Uniform = 26
    UniformId = 27
    SaturatedConversion = 28
    Stream = 29
    Location = 30
    Component = 31
    Index = 32
    Binding = 33
    DescriptorSet = 34
    Offset = 35
    XfbBuffer = 36
    XfbStride = 37
    FuncParamAttr = 38
    FPRoundingMode = 39
    FPFastMathMode = 40
    LinkageAttributes = 41
    NoContraction = 42
    InputAttachmentIndex = 43
    Alignment = 44
    MaxByteOffset = 45
    AlignmentId = 46
    MaxByteOffsetId = 47
    NoSignedWrap = 4469
    NoUnsignedWrap = 4470
    ExplicitInterpAMD = 4999
    OverrideCoverageNV = 5248
    PassthroughNV = 5250
    ViewportRelativeNV = 5252
    SecondaryViewportRelativeNV = 5256
    PerPrimitiveNV = 5271
    PerViewNV = 5272
    PerTaskNV = 5273
    PerVertexKHR = 5285
    PerVertexNV = 5285
    NonUniform = 5300
    NonUniformEXT = 5300
    RestrictPointer = 5355
    RestrictPointerEXT = 5355
    AliasedPointer = 5356
    AliasedPointerEXT = 5356
    BindlessSamplerNV = 5398
    BindlessImageNV = 5399
    BoundSamplerNV = 5400
    BoundImageNV = 5401
    SIMTCallINTEL = 5599
    ReferencedIndirectlyINTEL = 5602
    ClobberINTEL = 5607
    SideEffectsINTEL = 5608
    VectorComputeVariableINTEL = 5624
    FuncParamIOKindINTEL = 5625
    VectorComputeFunctionINTEL = 5626
    StackCallINTEL = 5627
    GlobalVariableOffsetINTEL = 5628
    CounterBuffer = 5634
    HlslCounterBufferGOOGLE = 5634
    HlslSemanticGOOGLE = 5635
    UserSemantic = 5635
    UserTypeGOOGLE = 5636
    FunctionRoundingModeINTEL = 5822
    FunctionDenormModeINTEL = 5823
    RegisterINTEL = 5825
    MemoryINTEL = 5826
    NumbanksINTEL = 5827
    BankwidthINTEL = 5828
    MaxPrivateCopiesINTEL = 5829
    SinglepumpINTEL = 5830
    DoublepumpINTEL = 5831
    MaxReplicatesINTEL = 5832
    SimpleDualPortINTEL = 5833
    MergeINTEL = 5834
    BankBitsINTEL = 5835
    ForcePow2DepthINTEL = 5836
    BurstCoalesceINTEL = 5899
    CacheSizeINTEL = 5900
    DontStaticallyCoalesceINTEL = 5901
    PrefetchINTEL = 5902
    StallEnableINTEL = 5905
    FuseLoopsInFunctionINTEL = 5907
    BufferLocationINTEL = 5921
    IOPipeStorageINTEL = 5944
    FunctionFloatingPointModeINTEL = 6080
    SingleElementVectorINTEL = 6085
    VectorComputeCallableFunctionINTEL = 6087
    MediaBlockIOINTEL = 6140


class BuiltIn(SPIRVEnum):
    Position = 0
    PointSize = 1
    ClipDistance = 3
    CullDistance = 4
    VertexId = 5
    InstanceId = 6
    PrimitiveId = 7
    InvocationId = 8
    Layer = 9
    ViewportIndex = 10
    TessLevelOuter = 11
    TessLevelInner = 12
    TessCoord = 13
    PatchVertices = 14
    FragCoord = 15
    PointCoord = 16
    FrontFacing = 17
    SampleId = 18
    SamplePosition = 19
    SampleMask = 20
    FragDepth = 22
    HelperInvocation = 23
    NumWorkgroups = 24
    WorkgroupSize = 25
    WorkgroupId = 26
    LocalInvocationId = 27
    GlobalInvocationId = 28
    LocalInvocationIndex = 29
    WorkDim = 30
    GlobalSize = 31
    EnqueuedWorkgroupSize = 32
    GlobalOffset = 33
    GlobalLinearId = 34
    SubgroupSize = 36
    SubgroupMaxSize = 37
    NumSubgroups = 38
    NumEnqueuedSubgroups = 39
    SubgroupId = 40
    SubgroupLocalInvocationId = 41
    VertexIndex = 42
    InstanceIndex = 43
    SubgroupEqMask = 4416
    SubgroupEqMaskKHR = 4416
    SubgroupGeMask = 4417
    SubgroupGeMaskKHR = 4417
    SubgroupGtMask = 4418
    SubgroupGtMaskKHR = 4418
    SubgroupLeMask = 4419
    SubgroupLeMaskKHR = 4419
    SubgroupLtMask = 4420
    SubgroupLtMaskKHR = 4420
    BaseVertex = 4424
    BaseInstance = 4425
    DrawIndex = 4426
    PrimitiveShadingRateKHR = 4432
    DeviceIndex = 4438
    ViewIndex = 4440
    ShadingRateKHR = 4444
    BaryCoordNoPerspAMD = 4992
    BaryCoordNoPerspCentroidAMD = 4993
    BaryCoordNoPerspSampleAMD = 4994
    BaryCoordSmoothAMD = 4995
    BaryCoordSmoothCentroidAMD = 4996
    BaryCoordSmoothSampleAMD = 4997
    BaryCoordPullModelAMD = 4998
    FragStencilRefEXT = 5014
    ViewportMaskNV = 5253
    SecondaryPositionNV = 5257
    SecondaryViewportMaskNV = 5258
    PositionPerViewNV = 5261
    ViewportMaskPerViewNV = 5262
    FullyCoveredEXT = 5264
    TaskCountNV = 5274
    PrimitiveCountNV = 5275
    PrimitiveIndicesNV = 5276
    ClipDistancePerViewNV = 5277
    CullDistancePerViewNV = 5278
    LayerPerViewNV = 5279
    MeshViewCountNV = 5280
    MeshViewIndicesNV = 5281
    BaryCoordKHR = 5286
    BaryCoordNV = 5286
    BaryCoordNoPerspKHR = 5287
    BaryCoordNoPerspNV = 5287
    FragSizeEXT = 5292
    FragmentSizeNV = 5292
    FragInvocationCountEXT = 5293
    InvocationsPerPixelNV = 5293
    LaunchIdKHR = 5319
    LaunchIdNV = 5319
    LaunchSizeKHR = 5320
    LaunchSizeNV = 5320
    WorldRayOriginKHR = 5321
    WorldRayOriginNV = 5321
    WorldRayDirectionKHR = 5322
    WorldRayDirectionNV = 5322
    ObjectRayOriginKHR = 5323
    ObjectRayOriginNV = 5323
    ObjectRayDirectionKHR = 5324
    ObjectRayDirectionNV = 5324
    RayTminKHR = 5325
    RayTminNV = 5325
    RayTmaxKHR = 5326
    RayTmaxNV = 5326
    InstanceCustomIndexKHR = 5327
    InstanceCustomIndexNV = 5327
    ObjectToWorldKHR = 5330
    ObjectToWorldNV = 5330
    WorldToObjectKHR = 5331
    WorldToObjectNV = 5331
    HitTNV = 5332
    HitKindKHR = 5333
    HitKindNV = 5333
    CurrentRayTimeNV = 5334
    IncomingRayFlagsKHR = 5351
    IncomingRayFlagsNV = 5351
    RayGeometryIndexKHR = 5352
    WarpsPerSMNV = 5374
    SMCountNV = 5375
    WarpIDNV = 5376
    SMIDNV = 5377


class SelectionControlShift(SPIRVEnum):
    Flatten = 0
    DontFlatten = 1


class SelectionControlMask(SPIRVEnum):
    NONE = 0
    Flatten = 1
    DontFlatten = 2


class LoopControlShift(SPIRVEnum):
    Unroll = 0
    DontUnroll = 1
    DependencyInfinite = 2
    DependencyLength = 3
    MinIterations = 4
    MaxIterations = 5
    IterationMultiple = 6
    PeelCount = 7
    PartialCount = 8
    InitiationIntervalINTEL = 16
    MaxConcurrencyINTEL = 17
    DependencyArrayINTEL = 18
    PipelineEnableINTEL = 19
    LoopCoalesceINTEL = 20
    MaxInterleavingINTEL = 21
    SpeculatedIterationsINTEL = 22
    NoFusionINTEL = 23


class LoopControlMask(SPIRVEnum):
    MaskNone = 0
    Unroll = 1
    DontUnroll = 2
    DependencyInfinite = 4
    DependencyLength = 8
    MinIterations = 16
    MaxIterations = 32
    IterationMultiple = 64
    PeelCount = 128
    PartialCount = 256
    InitiationIntervalINTEL = 65536
    MaxConcurrencyINTEL = 131072
    DependencyArrayINTEL = 262144
    PipelineEnableINTEL = 524288
    LoopCoalesceINTEL = 1048576
    MaxInterleavingINTEL = 2097152
    SpeculatedIterationsINTEL = 4194304
    NoFusionINTEL = 8388608


class FunctionControlShift(SPIRVEnum):
    Inline = 0
    DontInline = 1
    Pure = 2
    Const = 3
    OptNoneINTEL = 16


class FunctionControlMask(SPIRVEnum):
    NONE = 0
    Inline = 1
    DontInline = 2
    Pure = 4
    Const = 8
    # OptNoneINTEL = 65536


class MemorySemanticsShift(SPIRVEnum):
    Acquire = 1
    Release = 2
    AcquireRelease = 3
    SequentiallyConsistent = 4
    UniformMemory = 6
    SubgroupMemory = 7
    WorkgroupMemory = 8
    CrossWorkgroupMemory = 9
    AtomicCounterMemory = 10
    ImageMemory = 11
    OutputMemory = 12
    OutputMemoryKHR = 12
    MakeAvailable = 13
    MakeAvailableKHR = 13
    MakeVisible = 14
    MakeVisibleKHR = 14
    Volatile = 15


class MemorySemanticsMask(SPIRVEnum):
    MaskNone = 0
    Acquire = 2
    Release = 4
    AcquireRelease = 8
    SequentiallyConsistent = 16
    UniformMemory = 64
    SubgroupMemory = 128
    WorkgroupMemory = 256
    CrossWorkgroupMemory = 512
    AtomicCounterMemory = 1024
    ImageMemory = 2048
    OutputMemory = 4096
    OutputMemoryKHR = 4096
    MakeAvailable = 8192
    MakeAvailableKHR = 8192
    MakeVisible = 16384
    MakeVisibleKHR = 16384
    Volatile = 32768


class MemoryAccessShift(SPIRVEnum):
    Volatile = 0
    Aligned = 1
    Nontemporal = 2
    MakePointerAvailable = 3
    MakePointerAvailableKHR = 3
    MakePointerVisible = 4
    MakePointerVisibleKHR = 4
    NonPrivatePointer = 5
    NonPrivatePointerKHR = 5


class MemoryAccessMask(SPIRVEnum):
    MaskNone = 0
    Volatile = 1
    Aligned = 2
    Nontemporal = 4
    MakePointerAvailable = 8
    MakePointerAvailableKHR = 8
    MakePointerVisible = 16
    MakePointerVisibleKHR = 16
    NonPrivatePointer = 32
    NonPrivatePointerKHR = 32


class Scope(SPIRVEnum):
    CrossDevice = 0
    Device = 1
    Workgroup = 2
    Subgroup = 3
    Invocation = 4
    QueueFamily = 5
    QueueFamilyKHR = 5
    ShaderCallKHR = 6


class GroupOperation(SPIRVEnum):
    Reduce = 0
    InclusiveScan = 1
    ExclusiveScan = 2
    ClusteredReduce = 3
    PartitionedReduceNV = 6
    PartitionedInclusiveScanNV = 7
    PartitionedExclusiveScanNV = 8


class KernelEnqueueFlags(SPIRVEnum):
    NoWait = 0
    WaitKernel = 1
    WaitWorkGroup = 2


class KernelProfilingInfoShift(SPIRVEnum):
    CmdExecTime = 0


class KernelProfilingInfoMask(SPIRVEnum):
    MaskNone = 0
    CmdExecTime = 1


class Capability(SPIRVEnum):
    Matrix = 0
    Shader = 1
    Geometry = 2
    Tessellation = 3
    Addresses = 4
    Linkage = 5
    Kernel = 6
    Vector16 = 7
    Float16Buffer = 8
    Float16 = 9
    Float64 = 10
    Int64 = 11
    Int64Atomics = 12
    ImageBasic = 13
    ImageReadWrite = 14
    ImageMipmap = 15
    Pipes = 17
    Groups = 18
    DeviceEnqueue = 19
    LiteralSampler = 20
    AtomicStorage = 21
    Int16 = 22
    TessellationPointSize = 23
    GeometryPointSize = 24
    ImageGatherExtended = 25
    StorageImageMultisample = 27
    UniformBufferArrayDynamicIndexing = 28
    SampledImageArrayDynamicIndexing = 29
    StorageBufferArrayDynamicIndexing = 30
    StorageImageArrayDynamicIndexing = 31
    ClipDistance = 32
    CullDistance = 33
    ImageCubeArray = 34
    SampleRateShading = 35
    ImageRect = 36
    SampledRect = 37
    GenericPointer = 38
    Int8 = 39
    InputAttachment = 40
    SparseResidency = 41
    MinLod = 42
    Sampled1D = 43
    Image1D = 44
    SampledCubeArray = 45
    SampledBuffer = 46
    ImageBuffer = 47
    ImageMSArray = 48
    StorageImageExtendedFormats = 49
    ImageQuery = 50
    DerivativeControl = 51
    InterpolationFunction = 52
    TransformFeedback = 53
    GeometryStreams = 54
    StorageImageReadWithoutFormat = 55
    StorageImageWriteWithoutFormat = 56
    MultiViewport = 57
    SubgroupDispatch = 58
    NamedBarrier = 59
    PipeStorage = 60
    GroupNonUniform = 61
    GroupNonUniformVote = 62
    GroupNonUniformArithmetic = 63
    GroupNonUniformBallot = 64
    GroupNonUniformShuffle = 65
    GroupNonUniformShuffleRelative = 66
    GroupNonUniformClustered = 67
    GroupNonUniformQuad = 68
    ShaderLayer = 69
    ShaderViewportIndex = 70
    UniformDecoration = 71
    FragmentShadingRateKHR = 4422
    SubgroupBallotKHR = 4423
    DrawParameters = 4427
    WorkgroupMemoryExplicitLayoutKHR = 4428
    WorkgroupMemoryExplicitLayout8BitAccessKHR = 4429
    WorkgroupMemoryExplicitLayout16BitAccessKHR = 4430
    SubgroupVoteKHR = 4431
    StorageBuffer16BitAccess = 4433
    StorageUniformBufferBlock16 = 4433
    StorageUniform16 = 4434
    UniformAndStorageBuffer16BitAccess = 4434
    StoragePushConstant16 = 4435
    StorageInputOutput16 = 4436
    DeviceGroup = 4437
    MultiView = 4439
    VariablePointersStorageBuffer = 4441
    VariablePointers = 4442
    AtomicStorageOps = 4445
    SampleMaskPostDepthCoverage = 4447
    StorageBuffer8BitAccess = 4448
    UniformAndStorageBuffer8BitAccess = 4449
    StoragePushConstant8 = 4450
    DenormPreserve = 4464
    DenormFlushToZero = 4465
    SignedZeroInfNanPreserve = 4466
    RoundingModeRTE = 4467
    RoundingModeRTZ = 4468
    RayQueryProvisionalKHR = 4471
    RayQueryKHR = 4472
    RayTraversalPrimitiveCullingKHR = 4478
    RayTracingKHR = 4479
    Float16ImageAMD = 5008
    ImageGatherBiasLodAMD = 5009
    FragmentMaskAMD = 5010
    StencilExportEXT = 5013
    ImageReadWriteLodAMD = 5015
    Int64ImageEXT = 5016
    ShaderClockKHR = 5055
    SampleMaskOverrideCoverageNV = 5249
    GeometryShaderPassthroughNV = 5251
    ShaderViewportIndexLayerEXT = 5254
    ShaderViewportIndexLayerNV = 5254
    ShaderViewportMaskNV = 5255
    ShaderStereoViewNV = 5259
    PerViewAttributesNV = 5260
    FragmentFullyCoveredEXT = 5265
    MeshShadingNV = 5266
    ImageFootprintNV = 5282
    FragmentBarycentricKHR = 5284
    FragmentBarycentricNV = 5284
    ComputeDerivativeGroupQuadsNV = 5288
    FragmentDensityEXT = 5291
    ShadingRateNV = 5291
    GroupNonUniformPartitionedNV = 5297
    ShaderNonUniform = 5301
    ShaderNonUniformEXT = 5301
    RuntimeDescriptorArray = 5302
    RuntimeDescriptorArrayEXT = 5302
    InputAttachmentArrayDynamicIndexing = 5303
    InputAttachmentArrayDynamicIndexingEXT = 5303
    UniformTexelBufferArrayDynamicIndexing = 5304
    UniformTexelBufferArrayDynamicIndexingEXT = 5304
    StorageTexelBufferArrayDynamicIndexing = 5305
    StorageTexelBufferArrayDynamicIndexingEXT = 5305
    UniformBufferArrayNonUniformIndexing = 5306
    UniformBufferArrayNonUniformIndexingEXT = 5306
    SampledImageArrayNonUniformIndexing = 5307
    SampledImageArrayNonUniformIndexingEXT = 5307
    StorageBufferArrayNonUniformIndexing = 5308
    StorageBufferArrayNonUniformIndexingEXT = 5308
    StorageImageArrayNonUniformIndexing = 5309
    StorageImageArrayNonUniformIndexingEXT = 5309
    InputAttachmentArrayNonUniformIndexing = 5310
    InputAttachmentArrayNonUniformIndexingEXT = 5310
    UniformTexelBufferArrayNonUniformIndexing = 5311
    UniformTexelBufferArrayNonUniformIndexingEXT = 5311
    StorageTexelBufferArrayNonUniformIndexing = 5312
    StorageTexelBufferArrayNonUniformIndexingEXT = 5312
    RayTracingNV = 5340
    RayTracingMotionBlurNV = 5341
    VulkanMemoryModel = 5345
    VulkanMemoryModelKHR = 5345
    VulkanMemoryModelDeviceScope = 5346
    VulkanMemoryModelDeviceScopeKHR = 5346
    PhysicalStorageBufferAddresses = 5347
    PhysicalStorageBufferAddressesEXT = 5347
    ComputeDerivativeGroupLinearNV = 5350
    RayTracingProvisionalKHR = 5353
    CooperativeMatrixNV = 5357
    FragmentShaderSampleInterlockEXT = 5363
    FragmentShaderShadingRateInterlockEXT = 5372
    ShaderSMBuiltinsNV = 5373
    FragmentShaderPixelInterlockEXT = 5378
    DemoteToHelperInvocation = 5379
    DemoteToHelperInvocationEXT = 5379
    BindlessTextureNV = 5390
    SubgroupShuffleINTEL = 5568
    SubgroupBufferBlockIOINTEL = 5569
    SubgroupImageBlockIOINTEL = 5570
    SubgroupImageMediaBlockIOINTEL = 5579
    RoundToInfinityINTEL = 5582
    FloatingPointModeINTEL = 5583
    IntegerFunctions2INTEL = 5584
    FunctionPointersINTEL = 5603
    IndirectReferencesINTEL = 5604
    AsmINTEL = 5606
    AtomicFloat32MinMaxEXT = 5612
    AtomicFloat64MinMaxEXT = 5613
    AtomicFloat16MinMaxEXT = 5616
    VectorComputeINTEL = 5617
    VectorAnyINTEL = 5619
    ExpectAssumeKHR = 5629
    SubgroupAvcMotionEstimationINTEL = 5696
    SubgroupAvcMotionEstimationIntraINTEL = 5697
    SubgroupAvcMotionEstimationChromaINTEL = 5698
    VariableLengthArrayINTEL = 5817
    FunctionFloatControlINTEL = 5821
    FPGAMemoryAttributesINTEL = 5824
    FPFastMathModeINTEL = 5837
    ArbitraryPrecisionIntegersINTEL = 5844
    ArbitraryPrecisionFloatingPointINTEL = 5845
    UnstructuredLoopControlsINTEL = 5886
    FPGALoopControlsINTEL = 5888
    KernelAttributesINTEL = 5892
    FPGAKernelAttributesINTEL = 5897
    FPGAMemoryAccessesINTEL = 5898
    FPGAClusterAttributesINTEL = 5904
    LoopFuseINTEL = 5906
    FPGABufferLocationINTEL = 5920
    ArbitraryPrecisionFixedPointINTEL = 5922
    USMStorageClassesINTEL = 5935
    IOPipesINTEL = 5943
    BlockingPipesINTEL = 5945
    FPGARegINTEL = 5948
    DotProductInputAll = 6016
    DotProductInputAllKHR = 6016
    DotProductInput4x8Bit = 6017
    DotProductInput4x8BitKHR = 6017
    DotProductInput4x8BitPacked = 6018
    DotProductInput4x8BitPackedKHR = 6018
    DotProduct = 6019
    DotProductKHR = 6019
    BitInstructions = 6025
    AtomicFloat32AddEXT = 6033
    AtomicFloat64AddEXT = 6034
    LongConstantCompositeINTEL = 6089
    OptNoneINTEL = 6094
    AtomicFloat16AddEXT = 6095
    DebugInfoModuleINTEL = 6114


class RayFlagsShift(SPIRVEnum):
    OpaqueKHR = 0
    NoOpaqueKHR = 1
    TerminateOnFirstHitKHR = 2
    SkipClosestHitShaderKHR = 3
    CullBackFacingTrianglesKHR = 4
    CullFrontFacingTrianglesKHR = 5
    CullOpaqueKHR = 6
    CullNoOpaqueKHR = 7
    SkipTrianglesKHR = 8
    SkipAABBsKHR = 9


class RayFlagsMask(SPIRVEnum):
    MaskNone = 0
    OpaqueKHR = 1
    NoOpaqueKHR = 2
    TerminateOnFirstHitKHR = 4
    SkipClosestHitShaderKHR = 8
    CullBackFacingTrianglesKHR = 16
    CullFrontFacingTrianglesKHR = 32
    CullOpaqueKHR = 64
    CullNoOpaqueKHR = 128
    SkipTrianglesKHR = 256
    SkipAABBsKHR = 512


class RayQueryIntersection(SPIRVEnum):
    RayQueryCandidateIntersectionKHR = 0
    RayQueryCommittedIntersectionKHR = 1


class RayQueryCommittedIntersectionType(SPIRVEnum):
    RayQueryCommittedIntersectionNoneKHR = 0
    RayQueryCommittedIntersectionTriangleKHR = 1
    RayQueryCommittedIntersectionGeneratedKHR = 2


class RayQueryCandidateIntersectionType(SPIRVEnum):
    RayQueryCandidateIntersectionTriangleKHR = 0
    RayQueryCandidateIntersectionAABBKHR = 1


class FragmentShadingRateShift(SPIRVEnum):
    Vertical2Pixels = 0
    Vertical4Pixels = 1
    Horizontal2Pixels = 2
    Horizontal4Pixels = 3


class FragmentShadingRateMask(SPIRVEnum):
    MaskNone = 0
    Vertical2Pixels = 1
    Vertical4Pixels = 2
    Horizontal2Pixels = 4
    Horizontal4Pixels = 8


class FPDenormMode(SPIRVEnum):
    Preserve = 0
    FlushToZero = 1


class FPOperationMode(SPIRVEnum):
    IEEE = 0
    ALT = 1


class QuantizationModes(SPIRVEnum):
    TRN = 0
    TRN_ZERO = 1
    RND = 2
    RND_ZERO = 3
    RND_INF = 4
    RND_MIN_INF = 5
    RND_CONV = 6
    RND_CONV_ODD = 7


class OverflowModes(SPIRVEnum):
    WRAP = 0
    SAT = 1
    SAT_ZERO = 2
    SAT_SYM = 3


class PackedVectorFormat(SPIRVEnum):
    PackedVectorFormat4x8Bit = 0
    PackedVectorFormat4x8BitKHR = 0


Op = (
    {
        "OpNop": 0,
        "OpUndef": 1,
        "OpSourceContinued": 2,
        "OpSource": 3,
        "OpSourceExtension": 4,
        "OpName": 5,
        "OpMemberName": 6,
        "OpString": 7,
        "OpLine": 8,
        "OpExtension": 10,
        "OpExtInstImport": 11,
        "OpExtInst": 12,
        "OpMemoryModel": 14,
        "OpEntryPoint": 15,
        "OpExecutionMode": 16,
        "OpCapability": 17,
        "OpTypeVoid": 19,
        "OpTypeBool": 20,
        "OpTypeInt": 21,
        "OpTypeFloat": 22,
        "OpTypeVector": 23,
        "OpTypeMatrix": 24,
        "OpTypeImage": 25,
        "OpTypeSampler": 26,
        "OpTypeSampledImage": 27,
        "OpTypeArray": 28,
        "OpTypeRuntimeArray": 29,
        "OpTypeStruct": 30,
        "OpTypeOpaque": 31,
        "OpTypePointer": 32,
        "OpTypeFunction": 33,
        "OpTypeEvent": 34,
        "OpTypeDeviceEvent": 35,
        "OpTypeReserveId": 36,
        "OpTypeQueue": 37,
        "OpTypePipe": 38,
        "OpTypeForwardPointer": 39,
        "OpConstantTrue": 41,
        "OpConstantFalse": 42,
        "OpConstant": 43,
        "OpConstantComposite": 44,
        "OpConstantSampler": 45,
        "OpConstantNull": 46,
        "OpSpecConstantTrue": 48,
        "OpSpecConstantFalse": 49,
        "OpSpecConstant": 50,
        "OpSpecConstantComposite": 51,
        "OpSpecConstantOp": 52,
        "OpFunction": 54,
        "OpFunctionParameter": 55,
        "OpFunctionEnd": 56,
        "OpFunctionCall": 57,
        "OpVariable": 59,
        "OpImageTexelPointer": 60,
        "OpLoad": 61,
        "OpStore": 62,
        "OpCopyMemory": 63,
        "OpCopyMemorySized": 64,
        "OpAccessChain": 65,
        "OpInBoundsAccessChain": 66,
        "OpPtrAccessChain": 67,
        "OpArrayLength": 68,
        "OpGenericPtrMemSemantics": 69,
        "OpInBoundsPtrAccessChain": 70,
        "OpDecorate": 71,
        "OpMemberDecorate": 72,
        "OpDecorationGroup": 73,
        "OpGroupDecorate": 74,
        "OpGroupMemberDecorate": 75,
        "OpVectorExtractDynamic": 77,
        "OpVectorInsertDynamic": 78,
        "OpVectorShuffle": 79,
        "OpCompositeConstruct": 80,
        "OpCompositeExtract": 81,
        "OpCompositeInsert": 82,
        "OpCopyObject": 83,
        "OpTranspose": 84,
        "OpSampledImage": 86,
        "OpImageSampleImplicitLod": 87,
        "OpImageSampleExplicitLod": 88,
        "OpImageSampleDrefImplicitLod": 89,
        "OpImageSampleDrefExplicitLod": 90,
        "OpImageSampleProjImplicitLod": 91,
        "OpImageSampleProjExplicitLod": 92,
        "OpImageSampleProjDrefImplicitLod": 93,
        "OpImageSampleProjDrefExplicitLod": 94,
        "OpImageFetch": 95,
        "OpImageGather": 96,
        "OpImageDrefGather": 97,
        "OpImageRead": 98,
        "OpImageWrite": 99,
        "OpImage": 100,
        "OpImageQueryFormat": 101,
        "OpImageQueryOrder": 102,
        "OpImageQuerySizeLod": 103,
        "OpImageQuerySize": 104,
        "OpImageQueryLod": 105,
        "OpImageQueryLevels": 106,
        "OpImageQuerySamples": 107,
        "OpConvertFToU": 109,
        "OpConvertFToS": 110,
        "OpConvertSToF": 111,
        "OpConvertUToF": 112,
        "OpUConvert": 113,
        "OpSConvert": 114,
        "OpFConvert": 115,
        "OpQuantizeToF16": 116,
        "OpConvertPtrToU": 117,
        "OpSatConvertSToU": 118,
        "OpSatConvertUToS": 119,
        "OpConvertUToPtr": 120,
        "OpPtrCastToGeneric": 121,
        "OpGenericCastToPtr": 122,
        "OpGenericCastToPtrExplicit": 123,
        "OpBitcast": 124,
        "OpSNegate": 126,
        "OpFNegate": 127,
        "OpIAdd": 128,
        "OpFAdd": 129,
        "OpISub": 130,
        "OpFSub": 131,
        "OpIMul": 132,
        "OpFMul": 133,
        "OpUDiv": 134,
        "OpSDiv": 135,
        "OpFDiv": 136,
        "OpUMod": 137,
        "OpSRem": 138,
        "OpSMod": 139,
        "OpFRem": 140,
        "OpFMod": 141,
        "OpVectorTimesScalar": 142,
        "OpMatrixTimesScalar": 143,
        "OpVectorTimesMatrix": 144,
        "OpMatrixTimesVector": 145,
        "OpMatrixTimesMatrix": 146,
        "OpOuterProduct": 147,
        "OpDot": 148,
        "OpIAddCarry": 149,
        "OpISubBorrow": 150,
        "OpUMulExtended": 151,
        "OpSMulExtended": 152,
        "OpAny": 154,
        "OpAll": 155,
        "OpIsNan": 156,
        "OpIsInf": 157,
        "OpIsFinite": 158,
        "OpIsNormal": 159,
        "OpSignBitSet": 160,
        "OpLessOrGreater": 161,
        "OpOrdered": 162,
        "OpUnordered": 163,
        "OpLogicalEqual": 164,
        "OpLogicalNotEqual": 165,
        "OpLogicalOr": 166,
        "OpLogicalAnd": 167,
        "OpLogicalNot": 168,
        "OpSelect": 169,
        "OpIEqual": 170,
        "OpINotEqual": 171,
        "OpUGreaterThan": 172,
        "OpSGreaterThan": 173,
        "OpUGreaterThanEqual": 174,
        "OpSGreaterThanEqual": 175,
        "OpULessThan": 176,
        "OpSLessThan": 177,
        "OpULessThanEqual": 178,
        "OpSLessThanEqual": 179,
        "OpFOrdEqual": 180,
        "OpFUnordEqual": 181,
        "OpFOrdNotEqual": 182,
        "OpFUnordNotEqual": 183,
        "OpFOrdLessThan": 184,
        "OpFUnordLessThan": 185,
        "OpFOrdGreaterThan": 186,
        "OpFUnordGreaterThan": 187,
        "OpFOrdLessThanEqual": 188,
        "OpFUnordLessThanEqual": 189,
        "OpFOrdGreaterThanEqual": 190,
        "OpFUnordGreaterThanEqual": 191,
        "OpShiftRightLogical": 194,
        "OpShiftRightArithmetic": 195,
        "OpShiftLeftLogical": 196,
        "OpBitwiseOr": 197,
        "OpBitwiseXor": 198,
        "OpBitwiseAnd": 199,
        "OpNot": 200,
        "OpBitFieldInsert": 201,
        "OpBitFieldSExtract": 202,
        "OpBitFieldUExtract": 203,
        "OpBitReverse": 204,
        "OpBitCount": 205,
        "OpDPdx": 207,
        "OpDPdy": 208,
        "OpFwidth": 209,
        "OpDPdxFine": 210,
        "OpDPdyFine": 211,
        "OpFwidthFine": 212,
        "OpDPdxCoarse": 213,
        "OpDPdyCoarse": 214,
        "OpFwidthCoarse": 215,
        "OpEmitVertex": 218,
        "OpEndPrimitive": 219,
        "OpEmitStreamVertex": 220,
        "OpEndStreamPrimitive": 221,
        "OpControlBarrier": 224,
        "OpMemoryBarrier": 225,
        "OpAtomicLoad": 227,
        "OpAtomicStore": 228,
        "OpAtomicExchange": 229,
        "OpAtomicCompareExchange": 230,
        "OpAtomicCompareExchangeWeak": 231,
        "OpAtomicIIncrement": 232,
        "OpAtomicIDecrement": 233,
        "OpAtomicIAdd": 234,
        "OpAtomicISub": 235,
        "OpAtomicSMin": 236,
        "OpAtomicUMin": 237,
        "OpAtomicSMax": 238,
        "OpAtomicUMax": 239,
        "OpAtomicAnd": 240,
        "OpAtomicOr": 241,
        "OpAtomicXor": 242,
        "OpPhi": 245,
        "OpLoopMerge": 246,
        "OpSelectionMerge": 247,
        "OpLabel": 248,
        "OpBranch": 249,
        "OpBranchConditional": 250,
        "OpSwitch": 251,
        "OpKill": 252,
        "OpReturn": 253,
        "OpReturnValue": 254,
        "OpUnreachable": 255,
        "OpLifetimeStart": 256,
        "OpLifetimeStop": 257,
        "OpGroupAsyncCopy": 259,
        "OpGroupWaitEvents": 260,
        "OpGroupAll": 261,
        "OpGroupAny": 262,
        "OpGroupBroadcast": 263,
        "OpGroupIAdd": 264,
        "OpGroupFAdd": 265,
        "OpGroupFMin": 266,
        "OpGroupUMin": 267,
        "OpGroupSMin": 268,
        "OpGroupFMax": 269,
        "OpGroupUMax": 270,
        "OpGroupSMax": 271,
        "OpReadPipe": 274,
        "OpWritePipe": 275,
        "OpReservedReadPipe": 276,
        "OpReservedWritePipe": 277,
        "OpReserveReadPipePackets": 278,
        "OpReserveWritePipePackets": 279,
        "OpCommitReadPipe": 280,
        "OpCommitWritePipe": 281,
        "OpIsValidReserveId": 282,
        "OpGetNumPipePackets": 283,
        "OpGetMaxPipePackets": 284,
        "OpGroupReserveReadPipePackets": 285,
        "OpGroupReserveWritePipePackets": 286,
        "OpGroupCommitReadPipe": 287,
        "OpGroupCommitWritePipe": 288,
        "OpEnqueueMarker": 291,
        "OpEnqueueKernel": 292,
        "OpGetKernelNDrangeSubGroupCount": 293,
        "OpGetKernelNDrangeMaxSubGroupSize": 294,
        "OpGetKernelWorkGroupSize": 295,
        "OpGetKernelPreferredWorkGroupSizeMultiple": 296,
        "OpRetainEvent": 297,
        "OpReleaseEvent": 298,
        "OpCreateUserEvent": 299,
        "OpIsValidEvent": 300,
        "OpSetUserEventStatus": 301,
        "OpCaptureEventProfilingInfo": 302,
        "OpGetDefaultQueue": 303,
        "OpBuildNDRange": 304,
        "OpImageSparseSampleImplicitLod": 305,
        "OpImageSparseSampleExplicitLod": 306,
        "OpImageSparseSampleDrefImplicitLod": 307,
        "OpImageSparseSampleDrefExplicitLod": 308,
        "OpImageSparseSampleProjImplicitLod": 309,
        "OpImageSparseSampleProjExplicitLod": 310,
        "OpImageSparseSampleProjDrefImplicitLod": 311,
        "OpImageSparseSampleProjDrefExplicitLod": 312,
        "OpImageSparseFetch": 313,
        "OpImageSparseGather": 314,
        "OpImageSparseDrefGather": 315,
        "OpImageSparseTexelsResident": 316,
        "OpNoLine": 317,
        "OpAtomicFlagTestAndSet": 318,
        "OpAtomicFlagClear": 319,
        "OpImageSparseRead": 320,
        "OpSizeOf": 321,
        "OpTypePipeStorage": 322,
        "OpConstantPipeStorage": 323,
        "OpCreatePipeFromPipeStorage": 324,
        "OpGetKernelLocalSizeForSubgroupCount": 325,
        "OpGetKernelMaxNumSubgroups": 326,
        "OpTypeNamedBarrier": 327,
        "OpNamedBarrierInitialize": 328,
        "OpMemoryNamedBarrier": 329,
        "OpModuleProcessed": 330,
        "OpExecutionModeId": 331,
        "OpDecorateId": 332,
        "OpGroupNonUniformElect": 333,
        "OpGroupNonUniformAll": 334,
        "OpGroupNonUniformAny": 335,
        "OpGroupNonUniformAllEqual": 336,
        "OpGroupNonUniformBroadcast": 337,
        "OpGroupNonUniformBroadcastFirst": 338,
        "OpGroupNonUniformBallot": 339,
        "OpGroupNonUniformInverseBallot": 340,
        "OpGroupNonUniformBallotBitExtract": 341,
        "OpGroupNonUniformBallotBitCount": 342,
        "OpGroupNonUniformBallotFindLSB": 343,
        "OpGroupNonUniformBallotFindMSB": 344,
        "OpGroupNonUniformShuffle": 345,
        "OpGroupNonUniformShuffleXor": 346,
        "OpGroupNonUniformShuffleUp": 347,
        "OpGroupNonUniformShuffleDown": 348,
        "OpGroupNonUniformIAdd": 349,
        "OpGroupNonUniformFAdd": 350,
        "OpGroupNonUniformIMul": 351,
        "OpGroupNonUniformFMul": 352,
        "OpGroupNonUniformSMin": 353,
        "OpGroupNonUniformUMin": 354,
        "OpGroupNonUniformFMin": 355,
        "OpGroupNonUniformSMax": 356,
        "OpGroupNonUniformUMax": 357,
        "OpGroupNonUniformFMax": 358,
        "OpGroupNonUniformBitwiseAnd": 359,
        "OpGroupNonUniformBitwiseOr": 360,
        "OpGroupNonUniformBitwiseXor": 361,
        "OpGroupNonUniformLogicalAnd": 362,
        "OpGroupNonUniformLogicalOr": 363,
        "OpGroupNonUniformLogicalXor": 364,
        "OpGroupNonUniformQuadBroadcast": 365,
        "OpGroupNonUniformQuadSwap": 366,
        "OpCopyLogical": 400,
        "OpPtrEqual": 401,
        "OpPtrNotEqual": 402,
        "OpPtrDiff": 403,
        "OpTerminateInvocation": 4416,
        "OpSubgroupBallotKHR": 4421,
        "OpSubgroupFirstInvocationKHR": 4422,
        "OpSubgroupAllKHR": 4428,
        "OpSubgroupAnyKHR": 4429,
        "OpSubgroupAllEqualKHR": 4430,
        "OpSubgroupReadInvocationKHR": 4432,
        "OpTraceRayKHR": 4445,
        "OpExecuteCallableKHR": 4446,
        "OpConvertUToAccelerationStructureKHR": 4447,
        "OpIgnoreIntersectionKHR": 4448,
        "OpTerminateRayKHR": 4449,
        "OpSDot": 4450,
        "OpSDotKHR": 4450,
        "OpUDot": 4451,
        "OpUDotKHR": 4451,
        "OpSUDot": 4452,
        "OpSUDotKHR": 4452,
        "OpSDotAccSat": 4453,
        "OpSDotAccSatKHR": 4453,
        "OpUDotAccSat": 4454,
        "OpUDotAccSatKHR": 4454,
        "OpSUDotAccSat": 4455,
        "OpSUDotAccSatKHR": 4455,
        "OpTypeRayQueryKHR": 4472,
        "OpRayQueryInitializeKHR": 4473,
        "OpRayQueryTerminateKHR": 4474,
        "OpRayQueryGenerateIntersectionKHR": 4475,
        "OpRayQueryConfirmIntersectionKHR": 4476,
        "OpRayQueryProceedKHR": 4477,
        "OpRayQueryGetIntersectionTypeKHR": 4479,
        "OpGroupIAddNonUniformAMD": 5000,
        "OpGroupFAddNonUniformAMD": 5001,
        "OpGroupFMinNonUniformAMD": 5002,
        "OpGroupUMinNonUniformAMD": 5003,
        "OpGroupSMinNonUniformAMD": 5004,
        "OpGroupFMaxNonUniformAMD": 5005,
        "OpGroupUMaxNonUniformAMD": 5006,
        "OpGroupSMaxNonUniformAMD": 5007,
        "OpFragmentMaskFetchAMD": 5011,
        "OpFragmentFetchAMD": 5012,
        "OpReadClockKHR": 5056,
        "OpImageSampleFootprintNV": 5283,
        "OpGroupNonUniformPartitionNV": 5296,
        "OpWritePackedPrimitiveIndices4x8NV": 5299,
        "OpReportIntersectionKHR": 5334,
        "OpReportIntersectionNV": 5334,
        "OpIgnoreIntersectionNV": 5335,
        "OpTerminateRayNV": 5336,
        "OpTraceNV": 5337,
        "OpTraceMotionNV": 5338,
        "OpTraceRayMotionNV": 5339,
        "OpTypeAccelerationStructureKHR": 5341,
        "OpTypeAccelerationStructureNV": 5341,
        "OpExecuteCallableNV": 5344,
        "OpTypeCooperativeMatrixNV": 5358,
        "OpCooperativeMatrixLoadNV": 5359,
        "OpCooperativeMatrixStoreNV": 5360,
        "OpCooperativeMatrixMulAddNV": 5361,
        "OpCooperativeMatrixLengthNV": 5362,
        "OpBeginInvocationInterlockEXT": 5364,
        "OpEndInvocationInterlockEXT": 5365,
        "OpDemoteToHelperInvocation": 5380,
        "OpDemoteToHelperInvocationEXT": 5380,
        "OpIsHelperInvocationEXT": 5381,
        "OpConvertUToImageNV": 5391,
        "OpConvertUToSamplerNV": 5392,
        "OpConvertImageToUNV": 5393,
        "OpConvertSamplerToUNV": 5394,
        "OpConvertUToSampledImageNV": 5395,
        "OpConvertSampledImageToUNV": 5396,
        "OpSamplerImageAddressingModeNV": 5397,
        "OpSubgroupShuffleINTEL": 5571,
        "OpSubgroupShuffleDownINTEL": 5572,
        "OpSubgroupShuffleUpINTEL": 5573,
        "OpSubgroupShuffleXorINTEL": 5574,
        "OpSubgroupBlockReadINTEL": 5575,
        "OpSubgroupBlockWriteINTEL": 5576,
        "OpSubgroupImageBlockReadINTEL": 5577,
        "OpSubgroupImageBlockWriteINTEL": 5578,
        "OpSubgroupImageMediaBlockReadINTEL": 5580,
        "OpSubgroupImageMediaBlockWriteINTEL": 5581,
        "OpUCountLeadingZerosINTEL": 5585,
        "OpUCountTrailingZerosINTEL": 5586,
        "OpAbsISubINTEL": 5587,
        "OpAbsUSubINTEL": 5588,
        "OpIAddSatINTEL": 5589,
        "OpUAddSatINTEL": 5590,
        "OpIAverageINTEL": 5591,
        "OpUAverageINTEL": 5592,
        "OpIAverageRoundedINTEL": 5593,
        "OpUAverageRoundedINTEL": 5594,
        "OpISubSatINTEL": 5595,
        "OpUSubSatINTEL": 5596,
        "OpIMul32x16INTEL": 5597,
        "OpUMul32x16INTEL": 5598,
        "OpConstantFunctionPointerINTEL": 5600,
        "OpFunctionPointerCallINTEL": 5601,
        "OpAsmTargetINTEL": 5609,
        "OpAsmINTEL": 5610,
        "OpAsmCallINTEL": 5611,
        "OpAtomicFMinEXT": 5614,
        "OpAtomicFMaxEXT": 5615,
        "OpAssumeTrueKHR": 5630,
        "OpExpectKHR": 5631,
        "OpDecorateString": 5632,
        "OpDecorateStringGOOGLE": 5632,
        "OpMemberDecorateString": 5633,
        "OpMemberDecorateStringGOOGLE": 5633,
        "OpVmeImageINTEL": 5699,
        "OpTypeVmeImageINTEL": 5700,
        "OpTypeAvcImePayloadINTEL": 5701,
        "OpTypeAvcRefPayloadINTEL": 5702,
        "OpTypeAvcSicPayloadINTEL": 5703,
        "OpTypeAvcMcePayloadINTEL": 5704,
        "OpTypeAvcMceResultINTEL": 5705,
        "OpTypeAvcImeResultINTEL": 5706,
        "OpTypeAvcImeResultSingleReferenceStreamoutINTEL": 5707,
        "OpTypeAvcImeResultDualReferenceStreamoutINTEL": 5708,
        "OpTypeAvcImeSingleReferenceStreaminINTEL": 5709,
        "OpTypeAvcImeDualReferenceStreaminINTEL": 5710,
        "OpTypeAvcRefResultINTEL": 5711,
        "OpTypeAvcSicResultINTEL": 5712,
        "OpSubgroupAvcMceGetDefaultInterBaseMultiReferencePenaltyINTEL": 5713,
        "OpSubgroupAvcMceSetInterBaseMultiReferencePenaltyINTEL": 5714,
        "OpSubgroupAvcMceGetDefaultInterShapePenaltyINTEL": 5715,
        "OpSubgroupAvcMceSetInterShapePenaltyINTEL": 5716,
        "OpSubgroupAvcMceGetDefaultInterDirectionPenaltyINTEL": 5717,
        "OpSubgroupAvcMceSetInterDirectionPenaltyINTEL": 5718,
        "OpSubgroupAvcMceGetDefaultIntraLumaShapePenaltyINTEL": 5719,
        "OpSubgroupAvcMceGetDefaultInterMotionVectorCostTableINTEL": 5720,
        "OpSubgroupAvcMceGetDefaultHighPenaltyCostTableINTEL": 5721,
        "OpSubgroupAvcMceGetDefaultMediumPenaltyCostTableINTEL": 5722,
        "OpSubgroupAvcMceGetDefaultLowPenaltyCostTableINTEL": 5723,
        "OpSubgroupAvcMceSetMotionVectorCostFunctionINTEL": 5724,
        "OpSubgroupAvcMceGetDefaultIntraLumaModePenaltyINTEL": 5725,
        "OpSubgroupAvcMceGetDefaultNonDcLumaIntraPenaltyINTEL": 5726,
        "OpSubgroupAvcMceGetDefaultIntraChromaModeBasePenaltyINTEL": 5727,
        "OpSubgroupAvcMceSetAcOnlyHaarINTEL": 5728,
        "OpSubgroupAvcMceSetSourceInterlacedFieldPolarityINTEL": 5729,
        "OpSubgroupAvcMceSetSingleReferenceInterlacedFieldPolarityINTEL": 5730,
        "OpSubgroupAvcMceSetDualReferenceInterlacedFieldPolaritiesINTEL": 5731,
        "OpSubgroupAvcMceConvertToImePayloadINTEL": 5732,
        "OpSubgroupAvcMceConvertToImeResultINTEL": 5733,
        "OpSubgroupAvcMceConvertToRefPayloadINTEL": 5734,
        "OpSubgroupAvcMceConvertToRefResultINTEL": 5735,
        "OpSubgroupAvcMceConvertToSicPayloadINTEL": 5736,
        "OpSubgroupAvcMceConvertToSicResultINTEL": 5737,
        "OpSubgroupAvcMceGetMotionVectorsINTEL": 5738,
        "OpSubgroupAvcMceGetInterDistortionsINTEL": 5739,
        "OpSubgroupAvcMceGetBestInterDistortionsINTEL": 5740,
        "OpSubgroupAvcMceGetInterMajorShapeINTEL": 5741,
        "OpSubgroupAvcMceGetInterMinorShapeINTEL": 5742,
        "OpSubgroupAvcMceGetInterDirectionsINTEL": 5743,
        "OpSubgroupAvcMceGetInterMotionVectorCountINTEL": 5744,
        "OpSubgroupAvcMceGetInterReferenceIdsINTEL": 5745,
        "OpSubgroupAvcMceGetInterReferenceInterlacedFieldPolaritiesINTEL": 5746,
        "OpSubgroupAvcImeInitializeINTEL": 5747,
        "OpSubgroupAvcImeSetSingleReferenceINTEL": 5748,
        "OpSubgroupAvcImeSetDualReferenceINTEL": 5749,
        "OpSubgroupAvcImeRefWindowSizeINTEL": 5750,
        "OpSubgroupAvcImeAdjustRefOffsetINTEL": 5751,
        "OpSubgroupAvcImeConvertToMcePayloadINTEL": 5752,
        "OpSubgroupAvcImeSetMaxMotionVectorCountINTEL": 5753,
        "OpSubgroupAvcImeSetUnidirectionalMixDisableINTEL": 5754,
        "OpSubgroupAvcImeSetEarlySearchTerminationThresholdINTEL": 5755,
        "OpSubgroupAvcImeSetWeightedSadINTEL": 5756,
        "OpSubgroupAvcImeEvaluateWithSingleReferenceINTEL": 5757,
        "OpSubgroupAvcImeEvaluateWithDualReferenceINTEL": 5758,
        "OpSubgroupAvcImeEvaluateWithSingleReferenceStreaminINTEL": 5759,
        "OpSubgroupAvcImeEvaluateWithDualReferenceStreaminINTEL": 5760,
        "OpSubgroupAvcImeEvaluateWithSingleReferenceStreamoutINTEL": 5761,
        "OpSubgroupAvcImeEvaluateWithDualReferenceStreamoutINTEL": 5762,
        "OpSubgroupAvcImeEvaluateWithSingleReferenceStreaminoutINTEL": 5763,
        "OpSubgroupAvcImeEvaluateWithDualReferenceStreaminoutINTEL": 5764,
        "OpSubgroupAvcImeConvertToMceResultINTEL": 5765,
        "OpSubgroupAvcImeGetSingleReferenceStreaminINTEL": 5766,
        "OpSubgroupAvcImeGetDualReferenceStreaminINTEL": 5767,
        "OpSubgroupAvcImeStripSingleReferenceStreamoutINTEL": 5768,
        "OpSubgroupAvcImeStripDualReferenceStreamoutINTEL": 5769,
        "OpSubgroupAvcImeGetStreamoutSingleReferenceMajorShapeMotionVectorsINTEL": 5770,
        "OpSubgroupAvcImeGetStreamoutSingleReferenceMajorShapeDistortionsINTEL": 5771,
        "OpSubgroupAvcImeGetStreamoutSingleReferenceMajorShapeReferenceIdsINTEL": 5772,
        "OpSubgroupAvcImeGetStreamoutDualReferenceMajorShapeMotionVectorsINTEL": 5773,
        "OpSubgroupAvcImeGetStreamoutDualReferenceMajorShapeDistortionsINTEL": 5774,
        "OpSubgroupAvcImeGetStreamoutDualReferenceMajorShapeReferenceIdsINTEL": 5775,
        "OpSubgroupAvcImeGetBorderReachedINTEL": 5776,
        "OpSubgroupAvcImeGetTruncatedSearchIndicationINTEL": 5777,
        "OpSubgroupAvcImeGetUnidirectionalEarlySearchTerminationINTEL": 5778,
        "OpSubgroupAvcImeGetWeightingPatternMinimumMotionVectorINTEL": 5779,
        "OpSubgroupAvcImeGetWeightingPatternMinimumDistortionINTEL": 5780,
        "OpSubgroupAvcFmeInitializeINTEL": 5781,
        "OpSubgroupAvcBmeInitializeINTEL": 5782,
        "OpSubgroupAvcRefConvertToMcePayloadINTEL": 5783,
        "OpSubgroupAvcRefSetBidirectionalMixDisableINTEL": 5784,
        "OpSubgroupAvcRefSetBilinearFilterEnableINTEL": 5785,
        "OpSubgroupAvcRefEvaluateWithSingleReferenceINTEL": 5786,
        "OpSubgroupAvcRefEvaluateWithDualReferenceINTEL": 5787,
        "OpSubgroupAvcRefEvaluateWithMultiReferenceINTEL": 5788,
        "OpSubgroupAvcRefEvaluateWithMultiReferenceInterlacedINTEL": 5789,
        "OpSubgroupAvcRefConvertToMceResultINTEL": 5790,
        "OpSubgroupAvcSicInitializeINTEL": 5791,
        "OpSubgroupAvcSicConfigureSkcINTEL": 5792,
        "OpSubgroupAvcSicConfigureIpeLumaINTEL": 5793,
        "OpSubgroupAvcSicConfigureIpeLumaChromaINTEL": 5794,
        "OpSubgroupAvcSicGetMotionVectorMaskINTEL": 5795,
        "OpSubgroupAvcSicConvertToMcePayloadINTEL": 5796,
        "OpSubgroupAvcSicSetIntraLumaShapePenaltyINTEL": 5797,
        "OpSubgroupAvcSicSetIntraLumaModeCostFunctionINTEL": 5798,
        "OpSubgroupAvcSicSetIntraChromaModeCostFunctionINTEL": 5799,
        "OpSubgroupAvcSicSetBilinearFilterEnableINTEL": 5800,
        "OpSubgroupAvcSicSetSkcForwardTransformEnableINTEL": 5801,
        "OpSubgroupAvcSicSetBlockBasedRawSkipSadINTEL": 5802,
        "OpSubgroupAvcSicEvaluateIpeINTEL": 5803,
        "OpSubgroupAvcSicEvaluateWithSingleReferenceINTEL": 5804,
        "OpSubgroupAvcSicEvaluateWithDualReferenceINTEL": 5805,
        "OpSubgroupAvcSicEvaluateWithMultiReferenceINTEL": 5806,
        "OpSubgroupAvcSicEvaluateWithMultiReferenceInterlacedINTEL": 5807,
        "OpSubgroupAvcSicConvertToMceResultINTEL": 5808,
        "OpSubgroupAvcSicGetIpeLumaShapeINTEL": 5809,
        "OpSubgroupAvcSicGetBestIpeLumaDistortionINTEL": 5810,
        "OpSubgroupAvcSicGetBestIpeChromaDistortionINTEL": 5811,
        "OpSubgroupAvcSicGetPackedIpeLumaModesINTEL": 5812,
        "OpSubgroupAvcSicGetIpeChromaModeINTEL": 5813,
        "OpSubgroupAvcSicGetPackedSkcLumaCountThresholdINTEL": 5814,
        "OpSubgroupAvcSicGetPackedSkcLumaSumThresholdINTEL": 5815,
        "OpSubgroupAvcSicGetInterRawSadsINTEL": 5816,
        "OpVariableLengthArrayINTEL": 5818,
        "OpSaveMemoryINTEL": 5819,
        "OpRestoreMemoryINTEL": 5820,
        "OpArbitraryFloatSinCosPiINTEL": 5840,
        "OpArbitraryFloatCastINTEL": 5841,
        "OpArbitraryFloatCastFromIntINTEL": 5842,
        "OpArbitraryFloatCastToIntINTEL": 5843,
        "OpArbitraryFloatAddINTEL": 5846,
        "OpArbitraryFloatSubINTEL": 5847,
        "OpArbitraryFloatMulINTEL": 5848,
        "OpArbitraryFloatDivINTEL": 5849,
        "OpArbitraryFloatGTINTEL": 5850,
        "OpArbitraryFloatGEINTEL": 5851,
        "OpArbitraryFloatLTINTEL": 5852,
        "OpArbitraryFloatLEINTEL": 5853,
        "OpArbitraryFloatEQINTEL": 5854,
        "OpArbitraryFloatRecipINTEL": 5855,
        "OpArbitraryFloatRSqrtINTEL": 5856,
        "OpArbitraryFloatCbrtINTEL": 5857,
        "OpArbitraryFloatHypotINTEL": 5858,
        "OpArbitraryFloatSqrtINTEL": 5859,
        "OpArbitraryFloatLogINTEL": 5860,
        "OpArbitraryFloatLog2INTEL": 5861,
        "OpArbitraryFloatLog10INTEL": 5862,
        "OpArbitraryFloatLog1pINTEL": 5863,
        "OpArbitraryFloatExpINTEL": 5864,
        "OpArbitraryFloatExp2INTEL": 5865,
        "OpArbitraryFloatExp10INTEL": 5866,
        "OpArbitraryFloatExpm1INTEL": 5867,
        "OpArbitraryFloatSinINTEL": 5868,
        "OpArbitraryFloatCosINTEL": 5869,
        "OpArbitraryFloatSinCosINTEL": 5870,
        "OpArbitraryFloatSinPiINTEL": 5871,
        "OpArbitraryFloatCosPiINTEL": 5872,
        "OpArbitraryFloatASinINTEL": 5873,
        "OpArbitraryFloatASinPiINTEL": 5874,
        "OpArbitraryFloatACosINTEL": 5875,
        "OpArbitraryFloatACosPiINTEL": 5876,
        "OpArbitraryFloatATanINTEL": 5877,
        "OpArbitraryFloatATanPiINTEL": 5878,
        "OpArbitraryFloatATan2INTEL": 5879,
        "OpArbitraryFloatPowINTEL": 5880,
        "OpArbitraryFloatPowRINTEL": 5881,
        "OpArbitraryFloatPowNINTEL": 5882,
        "OpLoopControlINTEL": 5887,
        "OpFixedSqrtINTEL": 5923,
        "OpFixedRecipINTEL": 5924,
        "OpFixedRsqrtINTEL": 5925,
        "OpFixedSinINTEL": 5926,
        "OpFixedCosINTEL": 5927,
        "OpFixedSinCosINTEL": 5928,
        "OpFixedSinPiINTEL": 5929,
        "OpFixedCosPiINTEL": 5930,
        "OpFixedSinCosPiINTEL": 5931,
        "OpFixedLogINTEL": 5932,
        "OpFixedExpINTEL": 5933,
        "OpPtrCastToCrossWorkgroupINTEL": 5934,
        "OpCrossWorkgroupCastToPtrINTEL": 5938,
        "OpReadPipeBlockingINTEL": 5946,
        "OpWritePipeBlockingINTEL": 5947,
        "OpFPGARegINTEL": 5949,
        "OpRayQueryGetRayTMinKHR": 6016,
        "OpRayQueryGetRayFlagsKHR": 6017,
        "OpRayQueryGetIntersectionTKHR": 6018,
        "OpRayQueryGetIntersectionInstanceCustomIndexKHR": 6019,
        "OpRayQueryGetIntersectionInstanceIdKHR": 6020,
        "OpRayQueryGetIntersectionInstanceShaderBindingTableRecordOffsetKHR": 6021,
        "OpRayQueryGetIntersectionGeometryIndexKHR": 6022,
        "OpRayQueryGetIntersectionPrimitiveIndexKHR": 6023,
        "OpRayQueryGetIntersectionBarycentricsKHR": 6024,
        "OpRayQueryGetIntersectionFrontFaceKHR": 6025,
        "OpRayQueryGetIntersectionCandidateAABBOpaqueKHR": 6026,
        "OpRayQueryGetIntersectionObjectRayDirectionKHR": 6027,
        "OpRayQueryGetIntersectionObjectRayOriginKHR": 6028,
        "OpRayQueryGetWorldRayDirectionKHR": 6029,
        "OpRayQueryGetWorldRayOriginKHR": 6030,
        "OpRayQueryGetIntersectionObjectToWorldKHR": 6031,
        "OpRayQueryGetIntersectionWorldToObjectKHR": 6032,
        "OpAtomicFAddEXT": 6035,
        "OpTypeBufferSurfaceINTEL": 6086,
        "OpTypeStructContinuedINTEL": 6090,
        "OpConstantCompositeContinuedINTEL": 6091,
        "OpSpecConstantCompositeContinuedINTEL": 6092,
    },
)


class GLSLOpcodes(SPIRVEnum):
    Round = 1
    RoundEven = 2
    Trunc = 3
    FAbs = 4
    SAbs = 5
    FSign = 6
    SSign = 7
    Floor = 8
    Ceil = 9
    Fract = 10
    Radians = 11
    Degrees = 12
    Sin = 13
    Cos = 14
    Tan = 15
    Asin = 16
    Acos = 17
    Atan = 18
    Sinh = 19
    Cosh = 20
    Tanh = 21
    Asinh = 22
    Acosh = 23
    Atanh = 24
    Atan2 = 25
    Pow = 26
    Exp = 27
    Log = 28
    Exp2 = 29
    Log2 = 30
    Sqrt = 31
    InverseSqrt = 32
    Determinant = 33
    MatrixInverse = 34
    Modf = 35
    ModfStruct = 36
    FMin = 37
    UMin = 38
    SMin = 39
    Fmax = 40
    UMax = 41
    SMax = 42
    FClamp = 43
    UClamp = 44
    SClamp = 45
    FMix = 46
    UNDEF = 47  # Why is this not defined in the spec?
    Step = 48
    SmoothStep = 49
    Fma = 50
    Frexp = 51
    FrexpStruct = 52
    Ldexp = 53
    PackSnorm4x8 = 54
    PackUnorm4x8 = 55
    PackSnorm2x16 = 56
    PackUnorm2x16 = 57
    PackHalf2x16 = 58
    PackDouble2x32 = 59
    UnpackSnorm2x16 = 60
    UnpackUnorm2x16 = 61
    UnpackHalf2x16 = 62
    UnpackSnorm4x8 = 63
    UnpackUnorm4x8 = 64
    UnpackDouble2x32 = 65
    Length = 66
    Distance = 67
    Cross = 68
    Normalize = 69
    FaceForward = 70
    Reflect = 71
    Refract = 72
    FindILsb = 73
    FindSMsb = 74
    FindUMsb = 75
    InterpolateAtCentroid = 76
    InterpolateAtSample = 77
    InterpolateAtOffset = 78
    NMin = 79
    NMax = 80
    NClamp = 81
