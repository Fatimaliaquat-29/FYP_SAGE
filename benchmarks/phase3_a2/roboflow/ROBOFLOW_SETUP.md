# Roboflow setup: re-labelling the 298 held-out frames

**PROVISIONAL:** every score in this phase is provisional. The held-out labels follow no consistent written convention (spec: docs/LABELLING_SPEC.md, v0.1 draft). This re-label exists to fix that.

**Scope.** Only the 298 frames of `handlabels/round6_heldout` go to Roboflow, together with their current boxes. Nothing from any other dataset is uploaded. Training stays local. Nothing has been uploaded yet; only you can do that.

**Tools already installed (outside the repo).**
- roboflow CLI 1.7.1 in `D:\FYP\PROJECT FILES\_tools\venv_roboflow`.
- The CLI help it was checked against is in `cli_help.txt`, next to this file.

---

## STOP CONDITION: read before step 1

These frames show identifiable people. **Do not upload unless the project is Private.**

I could not confirm from Roboflow's docs whether the free plan allows Private projects. The docs pages I needed failed to load or returned 404. Historically, Roboflow's free plan has made datasets public. If the UI does not let you set this project to **Private**, stop and do not upload. Ask your supervisor about a paid or academic plan, or label locally instead (CVAT or labelImg on your own machine).

---

## 1. Browser steps (only you can do these)

1. Sign in or create an account at https://app.roboflow.com. Use a workspace for this project only.
2. Create a project:
   - Type: **Object Detection**.
   - Suggested name: `sage-heldout-retag`.
   - Annotation group: anything, for example `objects`.
3. **Confirm the project is Private.** Look in the project or workspace settings for its visibility, and check that it reads Private. If it cannot be Private, stop (see above).
4. **Turn on the data-use opt-out.** This is the setting that stops Roboflow using or licensing your uploaded data.
   - Its menu name is **UNKNOWN**: I could not verify it from the docs.
   - Look for it in the workspace settings (privacy, data, or licensing sections). Do not guess.
   - If you cannot find it, ask Roboflow support before uploading.
5. Write down two IDs:
   - The **workspace ID**: the part after `app.roboflow.com/` in the URL.
   - The **project ID**: the URL part after the workspace, for example `sage-heldout-retag`.
6. Get your **private API key**. The docs say it is at https://app.roboflow.com/settings/api. Do not paste it into any file or chat.

## 2. Set the key for this PowerShell session only

Open a new PowerShell window and run this. It asks for the key without showing or saving it:

```powershell
$s = Read-Host -AsSecureString -Prompt "Roboflow API key"
$env:ROBOFLOW_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR([Runtime.InteropServices.Marshal]::SecureStringToBSTR($s))
Remove-Variable s
```

Why not `$env:ROBOFLOW_API_KEY = "<paste>"`?
- PowerShell's PSReadLine saves typed commands to a history file on disk.
- Its built-in filter for secrets looks for `apikey`, not `API_KEY`, so the pasted key would most likely be written to that file.

Also do **not** run `roboflow auth login`. It stores the key in a config file. The upload script reads `$env:ROBOFLOW_API_KEY`, which is the CLI's documented default (`roboflow --help`: "default: $ROBOFLOW_API_KEY or config file").

When you are finished, remove the key from the session:

```powershell
Remove-Item Env:\ROBOFLOW_API_KEY
```

## 3. Upload (only after steps 1 and 2)

In the same PowerShell window:

```powershell
cd "D:\FYP\PROJECT FILES\main\benchmarks\phase3_a2\roboflow"
powershell -NoProfile -ExecutionPolicy Bypass -File .\upload_to_roboflow.ps1 -Workspace <workspace-id> -Project sage-heldout-retag -ConfirmConsent -ConfirmOptOut
```

The script refuses to run if any of these is missing:
- either of the two switches;
- the API key in the session;
- an exact retype of `<workspace-id>/sage-heldout-retag` at its prompt.

It prints the file count (298 images + 298 label files + data.yaml) and the destination before uploading. It never prints the key.

What it runs (syntax verified against `--help`):

```
roboflow -w <workspace> image upload upload_heldout -p <project> -b round6-heldout-retag-original-labels -r 3
```

- The images land in the **train** split (inferred from the `train/` folder).
- The existing boxes come in as the starting annotations.

## 4. Labelling

- Follow `docs/LABELLING_SPEC.md` (a copy is in `../review_pack/`).
- **Tags** (`occ`, `cover`, `lowlight`, `unsure`) go in `../review_pack/review_sheet.csv`, **not** in Roboflow. Per-box attributes are not documented for the YOLO export, so they would be lost or unreliable.
- Use `../review_pack/index.html` to page through the frames with the current boxes and a brightened panel for the dark frames.
- Fix boxes only. Do not add new classes.

## 5. Export

1. In the project, click **Generate / Create version**.
2. **Preprocessing: none.** Remove every default step. Roboflow often pre-selects Auto-Orient and Resize; check that the list is empty.
3. **Augmentation: none.** Check that the list is empty.
4. Before generating, check in the UI that the version will contain 298 images.
5. Export in **YOLOv8** format, choose "download zip", and save it to `D:\FYP\PROJECT FILES\main\benchmarks\phase3_a2\roboflow\export\`.
6. Unzip it into that folder, for example `export\sage-heldout-retag-1\`.

## 6. Check the export before using it

```powershell
& 'D:\FYP\PROJECT FILES\main\.venv2\Scripts\python.exe' "D:\FYP\PROJECT FILES\main\benchmarks\phase3_a2\roboflow\check_export.py" "D:\FYP\PROJECT FILES\main\benchmarks\phase3_a2\roboflow\export\sage-heldout-retag-1"
```

It must print `ALL PASS`. It checks:
- [ ] **class-name ORDER** in the export's `data.yaml` = the 13 names in `src/detection/sage_classes.py` order. Roboflow may reorder classes, for example alphabetically. If it does, the ids in every label file mean different classes. **Do not use the export until this passes.**
- [ ] image count = 298;
- [ ] every export image maps back to an original frame name (Roboflow renames files to `<stem>_jpg.rf.<hash>.jpg`);
- [ ] image dimensions unchanged (this catches a Resize or Auto-Orient step left on);
- [ ] every image has a label file, and every class id is in 0..12.

Then follow `rescore_instructions.md`.
