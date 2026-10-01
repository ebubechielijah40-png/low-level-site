# Final-year demonstration guide

A ten-minute demonstration should establish behaviour with observations, not directory counts.

1. **Create a workspace.** Show the password eye controls, validation, and coherent terminal styling. Explain that each account owns its drafts and boot images.
2. **Show the path.** Machine code uses the same RV32I architecture as assembly. C adds storage and function abstractions, Rust adds selected access rules, and Verilog introduces logic descriptions. The OS track states its x86 architecture switch.
3. **Decode one instruction.** Open the first machine lesson, predict x5 = 5, run, inspect the register, and find its word in Trace. Explain why words and byte order differ.
4. **Show the integrated lesson.** Open C arrays, read the explanation beside the editor, run its length/sum example, then change the loop to visit index four. Show the bounds error. Restore the starter.
5. **Test a component.** Select RAM in the personal-computer model. Rotate and zoom it. Run the deliberately incomplete configuration, fix the parity request, and show all three target checks. Explain why these are virtual registers.
6. **Show the equivalent assembly.** Switch the same lab to RV32I and demonstrate aligned SW writes. Compare state, rather than source appearance.
7. **Build an image.** Open Build an OS, change the literal boot message, run, save, download, and re-import the 512-byte image. Boot the saved bytes. Explain the BIOS signature and limited emulator.
8. **Explain the kernel milestone.** Show the freestanding C source, assembly entry, linker script, build command, and ELF header. State that a compatible loader/QEMU boot is additional evidence still to be obtained.
9. **Present evidence.** Run manage.py test and tools/verify_examples.py. Show the baseline defects and the exact execution contracts.
10. **State the scope.** No arbitrary native runner, physical hardware controller, full kernel host, or completed user study is claimed. Browser visual tests remain to be run locally; the provided script records real screenshots and interaction outcomes.

Likely defence questions:

- Why preserve Django? The existing auth, migrations, models, and routes provided a useful foundation; the defects were in execution, flow, content, and state tracking.
- Why a teaching interpreter? It keeps experiments local, inspectable, and bounded without launching untrusted native programs on the application server. The tradeoff is language completeness.
- Why two architectures? RV32I makes integer encodings clear; the separately labelled x86 lab demonstrates the BIOS boot convention. The switch is explicit.
- Why no lesson locks? The requested progression guides learning while every application lab remains available.
- How do you know a configuration passed? The server compares recorded register state with declared targets. The animation alone is not the check.
- Does passing an example prove mastery? No. Completion is a learner review record; further exercises and independent reasoning provide additional evidence.
- Is the quantum view a real device? No. It computes an ideal two-qubit state and exact probabilities, with a conceptual component view.
- What still needs evaluation? Browser behaviour and layout, user learning/usability outcomes, a real kernel boot, and production resource/security engineering.
