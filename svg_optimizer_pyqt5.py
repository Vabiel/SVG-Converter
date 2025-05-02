import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QCheckBox
from PyQt5.QtCore import Qt
import lxml.etree as ET
import gzip
import re
import subprocess
import shutil

# Ensure ~/.pub-cache/bin is in PATH
os.environ["PATH"] += os.pathsep + os.path.expanduser("~/.pub-cache/bin")
# Full path to vector_graphics_compiler
VGC_PATH = os.path.expanduser("~/.pub-cache/bin/vector_graphics_compiler")

def check_vec_dependencies():
    """Checks if vector_graphics_compiler is available globally."""
    try:
        # Try command first
        result = subprocess.run(['vector_graphics_compiler', '--help'], capture_output=True, text=True)
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        # Try full path
        try:
            result = subprocess.run([VGC_PATH, '--help'], capture_output=True, text=True)
            if result.returncode == 0:
                return True
            raise Exception(f"vector_graphics_compiler failed: {result.stderr}\n"
                            f"Tried full path: {VGC_PATH}\n"
                            "Ensure it is installed globally: dart pub global activate vector_graphics_compiler")
        except FileNotFoundError:
            raise Exception(f"vector_graphics_compiler not found.\n"
                            f"Command tried: vector_graphics_compiler\n"
                            f"Full path tried: {VGC_PATH}\n"
                            "Install it globally: dart pub global activate vector_graphics_compiler\n"
                            f"Current PATH: {os.environ['PATH']}")
        except Exception as e:
            raise Exception(f"Error checking vector_graphics_compiler: {e}\n"
                            f"Tried full path: {VGC_PATH}")
    except Exception as e:
        raise Exception(f"Error checking vector_graphics_compiler: {e}\n"
                        "Verify global installation: dart pub global activate vector_graphics_compiler")

def optimize_svg_content(svg_content):
    """Optimizes SVG content using lxml."""
    try:
        parser = ET.XMLParser(remove_comments=True, remove_blank_text=True)
        tree = ET.fromstring(svg_content.encode('utf-8'), parser)
        
        # Remove metadata
        for elem in tree.findall(".//{http://www.w3.org/2000/svg}metadata"):
            elem.getparent().remove(elem)

        # Remove unused namespaces
        nsmap = {k: v for k, v in tree.nsmap.items() if tree.findall(f".//{{{v}}}*") or k is None}
        if nsmap != tree.nsmap:
            new_root = ET.Element(tree.tag, nsmap=nsmap, attrib=tree.attrib)
            new_root.extend(tree)
            tree = ET.ElementTree(new_root)

        # Simplify IDs
        id_count = 0
        for elem in tree.findall(".//*[@id]"):
            id_count += 1
            elem.set("id", f"id_{id_count}")

        # Remove unnecessary attributes
        for elem in tree.iter():
            if "fill" in elem.attrib and elem.attrib["fill"] == "none":
                del elem.attrib["fill"]
            if "stroke" in elem.attrib and elem.attrib["stroke"] == "none":
                del elem.attrib["stroke"]

        # Serialize to string
        optimized_svg = ET.tostring(tree, encoding="unicode", method="xml", pretty_print=False)
        optimized_svg = re.sub(r'<\?xml[^>]*\?>\n?', "", optimized_svg)
        return optimized_svg
    except Exception as e:
        raise Exception(f"Error during optimization: {e}")

def compile_to_vec(input_path, output_path):
    """Compiles an SVG to .vec using vector_graphics_compiler."""
    try:
        # Try command first
        result = subprocess.run([
            'vector_graphics_compiler',
            '-i', input_path,
            '-o', output_path
        ], capture_output=True, text=True)
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        # Try full path
        try:
            result = subprocess.run([
                VGC_PATH,
                '-i', input_path,
                '-o', output_path
            ], capture_output=True, text=True)
            if result.returncode == 0:
                return True
            raise Exception(f"vector_graphics_compiler failed: {result.stderr}\n"
                            f"Tried full path: {VGC_PATH}")
        except FileNotFoundError:
            raise Exception(f"vector_graphics_compiler not found.\n"
                            f"Command tried: vector_graphics_compiler\n"
                            f"Full path tried: {VGC_PATH}\n"
                            "Install it globally: dart pub global activate vector_graphics_compiler\n"
                            f"Current PATH: {os.environ['PATH']}")
        except Exception as e:
            raise Exception(f"Error compiling to .vec: {e}\n"
                            f"Tried full path: {VGC_PATH}")
    except Exception as e:
        raise Exception(f"Error compiling to .vec: {e}")

class SVGOptimizerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('SVG Processor')
        self.setGeometry(100, 100, 600, 400)
        self.setAcceptDrops(True)

        # Main widget and layout
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Instructions
        self.instructions = QLabel('Drag and drop SVG files or folders here, or click the button below to select a folder.')
        self.instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.instructions)

        # Checkboxes
        self.optimize_checkbox = QCheckBox('Optimize SVG')
        self.optimize_checkbox.setChecked(True)  # Default: checked
        layout.addWidget(self.optimize_checkbox)

        self.svgz_checkbox = QCheckBox('Output as SVGZ (gzip-compressed)')
        layout.addWidget(self.svgz_checkbox)

        self.vec_checkbox = QCheckBox('Compile to Vec')
        layout.addWidget(self.vec_checkbox)

        # Select folder button
        self.select_button = QPushButton('Select Folder')
        self.select_button.clicked.connect(self.select_folder)
        layout.addWidget(self.select_button)

        # Status label
        self.status_label = QLabel('Ready')
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        paths = [url.toLocalFile() for url in urls]
        self.process_paths(paths)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder:
            self.process_paths([folder])

    def check_vec_dependencies(self):
        """Wrapper for global check_vec_dependencies."""
        return check_vec_dependencies()

    def optimize_svg_content(self, svg_content):
        """Wrapper for optimize_svg_content."""
        return optimize_svg_content(svg_content)

    def compile_to_vec(self, input_path, output_path):
        """Wrapper for compile_to_vec."""
        return compile_to_vec(input_path, output_path)

    def process_paths(self, paths):
        """Processes a list of file or folder paths."""
        if not (self.optimize_checkbox.isChecked() or self.svgz_checkbox.isChecked() or self.vec_checkbox.isChecked()):
            self.status_label.setText('Error: Select at least one of Optimize SVG, Output as SVGZ, or Compile to Vec')
            return

        # Check vec dependencies if needed
        if self.vec_checkbox.isChecked():
            try:
                self.check_vec_dependencies()
            except Exception as e:
                self.status_label.setText(f'Dependency error: {e}')
                return

        optimized_files = 0
        optimized_folders = 0
        optimize = self.optimize_checkbox.isChecked()
        svgz = self.svgz_checkbox.isChecked()
        vec = self.vec_checkbox.isChecked()

        for path in paths:
            if not os.path.exists(path):
                self.status_label.setText(f'Skip: {path} (does not exist)')
                continue
            if os.path.isdir(path):
                count = self.process_folder(path, optimize, svgz, vec)
                if count > 0:
                    optimized_folders += 1
                    self.status_label.setText(f'Processed {count} SVGs in folder {path}')
                else:
                    self.status_label.setText(f'No SVG files found in folder {path}')
            elif os.path.isfile(path) and path.lower().endswith(('.svg', '.svgz')):
                output_base = os.path.splitext(path)[0]
                if self.process_svg(path, output_base, optimize, svgz, vec):
                    optimized_files += 1
                    self.status_label.setText(f'Processed: {path}')
            else:
                self.status_label.setText(f'Skip: {path} (not an SVG file)')

        if optimized_files > 0 or optimized_folders > 0:
            self.status_label.setText(f'Total: {optimized_files} files and {optimized_folders} folders processed')
        else:
            self.status_label.setText('Nothing processed')

    def process_svg(self, input_path, output_base, optimize=False, svgz=False, vec=False):
        """Processes a single SVG file (optimize, convert to SVGZ, and/or compile to Vec)."""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()

            # Optimize if requested
            if optimize:
                svg_content = self.optimize_svg_content(svg_content)
                temp_svg = os.path.splitext(input_path)[0] + '_temp_optimized.svg'
                with open(temp_svg, 'w', encoding='utf-8') as f:
                    f.write(svg_content)
            else:
                temp_svg = input_path

            processed = False

            # Generate SVG output
            if optimize and not svgz and not vec:
                output_path = output_base + '_optimized.svg'
                shutil.copy(temp_svg, output_path)
                self.status_label.setText(f'Successfully processed (optimized SVG): {input_path} -> {output_path}')
                processed = True

            # Generate SVGZ output
            if svgz:
                output_path = output_base + ('_optimized.svgz' if optimize else '_compressed.svgz')
                with gzip.open(output_path, 'wb', compresslevel=9) as f:
                    f.write(svg_content.encode('utf-8'))
                self.status_label.setText(f'Successfully processed (SVGZ, {"optimized" if optimize else "compressed"}): {input_path} -> {output_path}')
                processed = True

            # Generate Vec output
            if vec:
                output_path = output_base + ('_optimized.vec' if optimize else '_compiled.vec')
                if self.compile_to_vec(temp_svg, output_path):
                    self.status_label.setText(f'Successfully processed (Vec, {"optimized" if optimize else "compiled"}): {input_path} -> {output_path}')
                    processed = True

            # Clean up temporary file
            if optimize and os.path.exists(temp_svg):
                os.remove(temp_svg)

            return processed
        except Exception as e:
            self.status_label.setText(f'Error processing {input_path}: {e}')
            return False

    def process_folder(self, folder_path, optimize=False, svgz=False, vec=False):
        """Processes all SVG files in a folder."""
        supported_extensions = ('.svg', '.svgz')
        processed = 0
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(supported_extensions):
                input_path = os.path.join(folder_path, filename)
                output_base = os.path.splitext(input_path)[0]
                if self.process_svg(input_path, output_base, optimize, svgz, vec):
                    processed += 1
        return processed

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SVGOptimizerGUI()
    ex.show()
    sys.exit(app.exec_())