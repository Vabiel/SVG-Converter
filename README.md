# SVG Converter

A Python-based tool for processing SVG files, supporting optimization, conversion to SVGZ (gzip-compressed), and compilation to Vec format for Flutter applications. The tool offers two interfaces:
- **Console-based**: `svg_optimizer_console.py` for command-line usage.
- **GUI-based**: `svg_optimizer_pyqt5.py` with a PyQt5 interface supporting drag-and-drop.

## Features
- **Optimize SVG**: Removes metadata, simplifies IDs, strips unnecessary attributes, and cleans up namespaces using `lxml`.
- **Convert to SVGZ**: Creates gzip-compressed SVGZ files for smaller file sizes.
- **Compile to Vec**: Converts SVG files to Flutter’s Vec format using `vector_graphics_compiler` for efficient rendering in Flutter apps.
- **Batch Processing**: Processes individual files or entire folders.
- **Cross-Platform**: Runs on macOS, Linux, and Windows.

## Prerequisites
- **Python 3.6+**: Required for running the scripts.
- **Dart**: Needed for installing `vector_graphics_compiler`.
- **Dependencies**:
    - Python packages: `lxml`, `PyQt5`, `Pillow`.
    - Global `vector_graphics_compiler` for Vec compilation.

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/SVG-Converter.git
   cd SVG-Converter
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python Dependencies**:
   ```bash
   pip install lxml PyQt5 Pillow
   ```

4. **Install vector_graphics_compiler Globally**:
   ```bash
   dart pub global activate vector_graphics_compiler
   ```
   Ensure `~/.pub-cache/bin` is in your PATH:
   ```bash
   echo 'export PATH="$PATH:$HOME/.pub-cache/bin"' >> ~/.zshrc  # or ~/.bashrc
   source ~/.zshrc
   ```
   Verify installation:
   ```bash
   vector_graphics_compiler --help
   ```

5. **Run the Setup Script** (optional):
   The included `run.sh` (or `run.bat` on Windows) automates dependency installation and script execution:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

## Usage
### Option 1: Console-Based (`svg_optimizer_console.py`)
Run the console script to process SVG files or folders via command-line arguments or interactive prompts.

- **Process a Single File**:
  ```bash
  python3 svg_optimizer_console.py --vec /path/to/file.svg
  ```
  Outputs: `file_compiled.vec` (or `_optimized.svg`/`_optimized.svgz` if `--optimize`/`--svgz` is used).

- **Process a Folder**:
  ```bash
  python3 svg_optimizer_console.py --folder /path/to/folder --optimize --svgz --vec
  ```
  Processes all `.svg` and `.svgz` files in the folder.

- **Interactive Mode**:
  ```bash
  python3 svg_optimizer_console.py
  ```
  Enter a file or folder path when prompted.

- **Options**:
    - `--optimize` (`-o`): Optimize SVG (default: True).
    - `--svgz` (`-z`): Output as SVGZ.
    - `--vec` (`-v`): Compile to Vec.
    - `--folder` (`-f`): Process all SVGs in a folder.

### Option 2: GUI-Based (`svg_optimizer_pyqt5.py`)
Run the GUI script for a graphical interface with drag-and-drop support.

- **Launch the GUI**:
  ```bash
  python3 svg_optimizer_pyqt5.py
  ```
  Or via `run.sh`:
  ```bash
  ./run.sh
  ```
  Select option `2`.

- **Usage**:
    - Drag and drop SVG files or folders onto the window.
    - Or click **Select Folder** to choose a folder.
    - Check desired options:
        - **Optimize SVG**: Optimize the SVG file.
        - **Output as SVGZ**: Create a compressed SVGZ file.
        - **Compile to Vec**: Compile to Vec format.
    - The status label shows processing results.

### Running with `run.sh`
The `run.sh` script simplifies setup and execution:
```bash
./run.sh
```
- Select `1` for console mode or `2` for GUI mode.
- For console mode, pass arguments:
  ```bash
  ./run.sh --vec /path/to/file.svg
  ```

## Vec Compilation for Flutter
To use Vec files in a Flutter project:
1. Add the Vec file to your `pubspec.yaml`:
   ```yaml
   flutter:
     assets:
       - assets/file_compiled.vec
   ```
2. Use the `VectorGraphic` widget:
   ```dart
   import 'package:flutter/material.dart';
   import 'package:vector_graphics/vector_graphics.dart';

   void main() {
     runApp(MaterialApp(
       home: Scaffold(
         body: Center(
           child: VectorGraphic(
             loader: AssetBytesLoader('assets/file_compiled.vec'),
             width: 300,
             height: 300,
           ),
         ),
       ),
     ));
   }
   ```
3. Run the app:
   ```bash
   flutter run
   ```

## Troubleshooting
- **vector_graphics_compiler not found**:
    - Verify installation: `vector_graphics_compiler --help`.
    - Ensure `~/.pub-cache/bin` is in PATH.
    - Reinstall: `dart pub global activate vector_graphics_compiler`.
- **PyQt5 issues**:
    - Reinstall: `pip install PyQt5`.
    - Ensure Python 3.6+.
- **SVG processing errors**:
    - Check SVG validity (open in a browser or Inkscape).
    - Ensure file permissions: `chmod +r file.svg`.
- **PATH issues**:
    - Add `~/.pub-cache/bin` to PATH permanently (see Installation step 4).

## Contributing
Contributions are welcome! Please:
1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request with clear descriptions.

## License
[MIT License](LICENSE)