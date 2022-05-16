# Changelog
All notable changes to this project will be documented in this file. See [conventional commits](https://www.conventionalcommits.org/) for commit guidelines.

- - -
## v1.3.0 - 2022-05-16
#### Bug Fixes
- **(brokerage)** limit fetching of mismatched shaders to current generator version - (bcd3142) - Rayan Hatout
- **(brokerage)** remove extraneous comma in buffer dump insert query - (b0fb57d) - Rayan Hatout
- **(brokerage)** replace use of pickle by dill - (68e122d) - Rayan Hatout
- **(brokerage)** remove extraneous quote in pending shaders query - (56afd6a) - Rayan Hatout
#### Miscellaneous Chores
- **(version)** v1.2.0 - (92964bd) - Rayan Hatout

- - -

## v1.2.0 - 2022-05-15
#### Bug Fixes
- **(infra)** remove extraneous comma in DB schema - (05e5932) - Rayan Hatout
#### Features
- **(all)** implement SPIR-V parser - (9ecced7) - Rayan Hatout
- **(fuzzer)** implement random mutations - (a1a5ca8) - Rayan Hatout
- **(reducer)** implement interestingness-guided automatic reduction, only uses statics checks for now - (bad987a) - Rayan Hatout
- **(runner)** add debug prints as a workaround for not being able to install DataDog on DoC machines - (5ed4a5c) - Rayan Hatout
#### Style
- **(all)** clean-up imports - (1ad4636) - Rayan Hatout

- - -
## v1.1.0 - 2022-05-03
#### Bug Fixes
- **(infra)** add missing comma in Terraform config - (8cb81f0) - Rayan Hatout
- **(runner)** remove extraneous comma in DML query - (05584f8) - Rayan Hatout
- **(runner)** group predicates correctly in DB query for new shaders to run - (01a0448) - Rayan Hatout
#### Features
- **(infra)** record the shader revision in DB - (b0df8c5) - Rayan Hatout

- - -

## v1.0.0 - 2022-05-01
#### Bug Fixes
- **(ci)** add quotes around image name in deploy job - (f968ead) - Rayan Hatout
- **(cloud-build)** use GNU version of base64 in cloud starttup script - (d1393f7) - Rayan Hatout
- **(docker)** add auto-accept flag in apt-get install for jq - (244da82) - Rayan Hatout
- **(infra)** ensure that automatic versioning doesn't break in CI environments - (1f837b7) - Rayan Hatout
- **(infra)** add missing comma in GCE deploy command - (6d0a39b) - Rayan Hatout
- **(infra)** inject Google Cloud credentials when running the Docker image - (2339b55) - Rayan Hatout
- **(infra)** update service account email for Google Compute Engine instance - (b63728f) - Rayan Hatout
- **(infra)** allow Compute Engine to be stopped for updates - (54fb1f5) - Rayan Hatout
- **(scripts)** use local Vulkan during Amber compilation - (42562d2) - Rayan Hatout
#### Build system
- **(docker)** add installation of jq in Dockerfile - (3a90b4a) - Rayan Hatout
#### Continuous Integration
- **(infra)** disable caching of Terraform plan - (db0d46a) - Rayan Hatout
- **(infra)** silence Terraform output - (81187e6) - Rayan Hatout
#### Features
- **(all)** prepare SPIRVSmith to run indefinitely on Google Cloud - (a986273) - Rayan Hatout
- **(fuzzer)** disable GLSL operations for which we can't guarantee determinism - (7799905) - Rayan Hatout
- **(fuzzer)** implement reconditioning of GLSL instructions - (f807ad3) - Rayan Hatout
- **(infra)** record SPIRVSmith version in DB of generated shaders - (3f5f8ec) - Rayan Hatout
- **(infra)** update BigQuery schema to record the number of Amber buffers to dump - (350820e) - Rayan Hatout
- **(infra)** update the database scheme - (de959b5) - Rayan Hatout
- **(infra)** introduce DataDog tracing and make BigQuery tables permanent - (aae9f36) - Rayan Hatout
- **(infra)** replace use of BigQuery by Firestore to store run configurations - (de567ae) - Rayan Hatout
- **(infra)** sunset usage of PubSub and use BigQuery as a single source of truth to synchronise primary and secondary nodes - (3fb87d8) - Rayan Hatout
- **(infra)** update service account for Compute Engine instance - (80a9934) - Rayan Hatout
- **(infra)** update cloud script to dynamically enable DataDog logging - (841c6fb) - Rayan Hatout
- **(infra)** replace custom network interface by default in Google Cloud configuration - (2dbbe3d) - Rayan Hatout
- **(monitoring)** enable stdout logging in Compute Engine - (309087d) - Rayan Hatout
- **(runner)** add the ability of forcing the runner to use the CPU - (815b8fe) - Rayan Hatout
- **(runner)** make sure Amber runner doesn't ignore GPUs that are in use - (3a47e1c) - Rayan Hatout
- **(runner)** implement shader fetching and DB updating in the Amber runner server - (d6f81ee) - Rayan Hatout
- **(scripts)** replace use of Ninja by Make in dependency-fetching scripts - (06a769b) - Rayan Hatout
#### Miscellaneous Chores
- **(dependencies)** roll dependencies - (17db894) - Rayan Hatout
- **(fuzzer)** prepend SPIRVSmith magic number at the beginning of generated files alongside additional debug info - (6be6f89) - Rayan Hatout
- move Amber server to top-level - (5a618f8) - Rayan Hatout

- - -

## v0.4.0 - 2022-04-19
#### Documentation
- update CITATION.cff for v0.4.0 - (a3dec92) - Rayan Hatout
- update CITATION.cff for v0.3.0 - (241d06e) - Rayan Hatout
#### Features
- **(fuzzer)** implement usage of OpExtension, OpExtInstImport and OpExtInst; modify fuzzer logic to include the GLSL extension - (6cba185) - Rayan Hatout
- **(fuzzer)** add a configuration switch to enable/disable inclusion of operators from the GLSL extension when fuzzing - (91f867e) - Rayan Hatout
- **(fuzzer)** implement fuzzing of the GLSL extension operators - (131611b) - Rayan Hatout
- **(fuzzer)** define enum used to lookup opcode IDs in the GLSL extension - (9a2832c) - Rayan Hatout
#### Style
- **(all)** clean up unused imports - (68c47aa) - Rayan Hatout
- **(fuzzer)** clean up unused imports in extension.py - (96eea50) - Rayan Hatout
- **(fuzzer)** simplify the predicate system - (dd60a22) - Rayan Hatout
- **(fuzzer)** reduce duplicate code in predicates - (6b46c92) - Rayan Hatout

- - -

## v0.3.0 - 2022-04-18
#### Bug Fixes
- **(fuzzer)** avoid redifinition of built-in object in OpStore - (2c2114c) - Rayan Hatout
- **(fuzzer)** rename MaskNone to NONE in SelectionControlMask SPIR-V enum to avoid assembly failure - (0871215) - Rayan Hatout
#### Features
- **(dependencies)** update dependencies script to additionally build spirv-cross after building spirv-tools - (f577593) - Rayan Hatout
- **(fuzzer)** implement OpAccessChain and refactor memory operators - (6aefb1b) - Rayan Hatout
#### Style
- **(all)** clean up unused imports - (f7531fb) - Rayan Hatout

- - -

## v0.2.0 - 2022-04-18
#### Bug Fixes
- **(fuzzer)** fix OpCopyObject accidentally renamed - (56f3fef) - Rayan Hatout
#### Documentation
- **(badges)** add DOI badge - (9f4ac4e) - Rayan Hatout
#### Features
- **(repo)** automatically push tags on a cog release - (aac8761) - Rayan Hatout
#### Miscellaneous Chores
- **(repo)** add a CITATION.cff file - (bbed315) - Rayan Hatout
#### Style
- **(all)** add missing newline in scripts and CHANGELOG - (201ad88) - Rayan Hatout

- - -

## 0.1.0 - 2022-04-18
#### Bug Fixes
- **(fuzzer)** avoid redefinition of builtins object and type when fuzzing composite operators - (7e2643b) - Rayan Hatout
- **(fuzzer)** fix a bug in OpMatrixTimesMatrix where operands were in the wrong order - (8442c8d) - Rayan Hatout
- **(fuzzer)** fix a few bugs related to linear algebra operators - (1fc6ef4) - Rayan Hatout
- **(fuzzer)** fix linear algebra nodes not being imported at runtime - (5091a76) - Rayan Hatout
- **(fuzzer)** replace use of pseudo-random generator by system random generator - (fa95d3c) - Rayan Hatout
- **(fuzzer)** fix a bug related to mismanaged scopes in nested blocks - (cc57e7b) - Rayan Hatout
- **(poetry)** manually add google-cloud transitive dependencies - (fd1882d) - Rayan Hatout
- **(tests)** fix test flakiness - (6846733) - Rayan Hatout
- **(tests)** fix implementation of tests that weren't updated after the change in type classification - (3113867) - Rayan Hatout
- **(tests)** refactor tests to make sure they don't start the webserver and upload data to the cloud - (a11b1bf) - Rayan Hatout
#### Build system
- **(docker)** update Dockerfile - (c505e45) - Rayan Hatout
- add Dockerization and Terraform-managed infra - (1bf5157) - Rayan Hatout
#### Continuous Integration
- **(infra)** add BiqQuery instance and PubSub to infra - (a09f17d) - Rayan Hatout
- **(infra)** use Google Compute Engine instead of Google Kubernetes Engine for deployment - (9576130) - Rayan Hatout
- **(infra)** update Actions to include Terraform deployment - (59d61aa) - Rayan Hatout
- modify build & test GitHub job to not wait on infra - (6ca1ba1) - Rayan Hatout
- Modify GitHub Action to not apply infrastructure changes on pull request - (1f9efb4) - Rayan Hatout
- Modify GitHub Action to not deploy on pull request - (a1720df) - Rayan Hatout
- pin the FOSSA Action version - (8e45329) - Rayan Hatout
- update GitHub Action to use the short SHA when tagging Docker images - (bf7dfaa) - Rayan Hatout
- perform initial setup of GitHub Actions - (bc9e6b7) - Rayan Hatout
#### Documentation
- **(badges)** update FOSSA badges - (6fe42bf) - Rayan Hatout
- **(repo)** add cloud infrastructure to README - (7b34112) - Rayan Hatout
- **(repo)** add explanations of differential testing and program reconditioning in README - (7b73178) - Rayan Hatout
- **(repo)** create CODE_OF_CONDUCT.md - (e956582) - Rayan Hatout
- **(repo)** add build status, license, and test coverage badges to README - (7e03ea6) - Rayan Hatout
- update reconditioning example in README - (bfbb4fa) - Rayan Hatout
#### Features
- **(all)** add some tests, do a whole project refactor, add DataDog monitoring, and fix some bugs - (47a4f83) - Rayan Hatout
- **(ambergen)** implement generation of structs by the Amber generator - (17bc7a2) - Rayan Hatout
- **(dependencies)** add scripts to roll dependencies - (286ece9) - Rayan Hatout
- **(fuzzer)** implement fuzzing of OpCompositeExtract, OpCompositeInsert, OpCopyObject, and OpTranspose - (a133067) - Rayan Hatout
- **(fuzzer)** implement fuzzing of linear algebra operators - (904d0dd) - Rayan Hatout
- **(fuzzer)** implement OpDecorate and OpMemberDecorate instructions, remove hardcoded annotations in the fuzzing server, and implement a shared __str__ method for SPIR-V enums - (35cdf01) - Rayan Hatout
- **(fuzzer)** perform a project-wide refactoring and implement fuzzing of vector access/insert operations - (04e6075) - Rayan Hatout
- **(fuzzer)** implement fuzzing of composite constants and fix a bug related to operand finding - (07c06c4) - Rayan Hatout
- **(fuzzer)** implement fuzzing of type conversion operators - (b71a75e) - Rayan Hatout
- **(fuzzer)** implement fuzzing of bitwise operators and a more fine-grained parametrization of randomness - (c81d2be) - Rayan Hatout
- **(fuzzer)** implement fuzzing of logic operators and the ability to parametrize randomness - (8e1123e) - Rayan Hatout
- **(fuzzer)** use Hydra to configure the fuzzer and add SPIRV coverage in README - (77fb560) - Rayan Hatout
- **(fuzzer)** implement fuzzing of scalar types/constants, arithmetic operators, and memory operators - (576d01c) - Rayan Hatout
- **(fuzzer)** define SPIR-V enums and universal limits - (fc4a054) - Rayan Hatout
- **(repo)** Initialise cog for conventional commits - (52f7511) - Rayan Hatout
- **(repo)** set up pre-commit hooks for reformating and linting - (efea705) - Rayan Hatout
#### Miscellaneous Chores
- **(dependencies)** roll dependencies - (1810116) - Rayan Hatout
- **(poetry)** update poetry.lock - (335acae) - Rayan Hatout
- **(poetry)** remove unused dependencies in Poetry configuration - (126bef5) - Rayan Hatout
- **(repo)** add templates for issues - (806d778) - Rayan Hatout
- **(repo)** set up git LFS - (d93b0ce) - Rayan Hatout
#### Refactoring
- **(fuzzer)** refactor arithmetic operators into different files to reduce complexity - (f709cef) - Rayan Hatout
- **(tests)** refactor tests to use the context object to generate JIT constants - (ee20603) - Rayan Hatout
#### Style
- **(all)** clean up unused imports - (bcbfe46) - Rayan Hatout
- **(all)** mark static methods with the corresponding decorator - (5b9a443) - Rayan Hatout
- **(all)** replace type hints with their generic alias type where possible - (ee8657e) - Rayan Hatout
- **(all)** clean up unused imports - (180d2ec) - Rayan Hatout
- **(all)** clean up unused imports - (133ca47) - Rayan Hatout
- **(docker)** pin poetry version in Dockerfile - (6c57ad5) - Rayan Hatout
- **(fuzzer)** clean up unused imports - (b5a5b90) - Rayan Hatout
- **(tests)** reformat tests and clean up unusued imports - (14cdd3d) - Rayan Hatout
#### Tests
- implement tests related to composite operators - (799b711) - Rayan Hatout
- implement tests for the SPIRVSmith type system - (b2c4f1e) - Rayan Hatout
- implement tests for linear algebra fuzz nodes - (fd5a678) - Rayan Hatout
- implement tests for memory and constant operators - (abcdeea) - Rayan Hatout

- - -

Changelog generated by [cocogitto](https://github.com/cocogitto/cocogitto).
