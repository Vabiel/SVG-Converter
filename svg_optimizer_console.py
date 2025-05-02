import os
import argparse
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

def process_svg(input_path, output_base, optimize=False, svgz=False, vec=False):
    """Processes a single SVG file (optimize, convert to SVGZ, and/or compile to Vec)."""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()

        # Optimize if requested
        if optimize:
            svg_content = optimize_svg_content(svg_content)
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
            print(f'Successfully processed (optimized SVG): {input_path} -> {output_path}')
            processed = True

        # Generate SVGZ output
        if svgz:
            output_path = output_base + ('_optimized.svgz' if optimize else '_compressed.svgz')
            with gzip.open(output_path, 'wb', compresslevel=9) as f:
                f.write(svg_content.encode('utf-8'))
            print(f'Successfully processed (SVGZ, {"optimized" if optimize else "compressed"}): {input_path} -> {output_path}')
            processed = True

        # Generate Vec output
        if vec:
            output_path = output_base + ('_optimized.vec' if optimize else '_compiled.vec')
            if compile_to_vec(temp_svg, output_path):
                print(f'Successfully processed (Vec, {"optimized" if optimize else "compiled"}): {input_path} -> {output_path}')
                processed = True

        # Clean up temporary file
        if optimize and os.path.exists(temp_svg):
            os.remove(temp_svg)

        return processed
    except Exception as e:
        print(f'Error processing {input_path}: {e}')
        return False

def process_folder(folder_path, optimize=False, svgz=False, vec=False):
    """Processes all SVG files in a folder."""
    supported_extensions = ('.svg', '.svgz')
    processed = 0
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(supported_extensions):
            input_path = os.path.join(folder_path, filename)
            output_base = os.path.splitext(input_path)[0]
            if process_svg(input_path, output_base, optimize=optimize, svgz=svgz, vec=vec):
                processed += 1
    return processed

def prompt_for_path():
    """Prompts the user for a file or folder path."""
    print("Enter a file or folder path to process (or press Enter to exit):")
    path = input().strip()
    if not path:
        return None
    if not os.path.exists(path):
        print(f'Error: {path} does not exist')
        return None
    return path

def main():
    parser = argparse.ArgumentParser(description='SVG File Processor')
    parser.add_argument('paths', nargs='*', help='Paths to SVG files or folders to process')
    parser.add_argument('--folder', '-f', help='Path to the folder to process all SVGs in it')
    parser.add_argument('--optimize', '-o', action='store_true', default=True, help='Optimize SVG files (default: True)')
    parser.add_argument('--svgz', '-z', action='store_true', help='Output as SVGZ (gzip-compressed)')
    parser.add_argument('--vec', '-v', action='store_true', help='Compile to Vec format')
    args = parser.parse_args()

    # Validate that at least one operation is requested
    if not (args.optimize or args.svgz or args.vec):
        print("Error: At least one of --optimize, --svgz, or --vec must be specified.")
        return

    # Check for vec dependencies if --vec is used
    if args.vec:
        try:
            check_vec_dependencies()
        except Exception as e:
            print(f"Dependency error: {e}")
            return

    # Initialize paths to process
    paths_to_process = args.paths
    folder_to_process = args.folder
    optimize = args.optimize
    svgz_output = args.svgz
    vec_output = args.vec

    # If no arguments provided, prompt for a path
    if not paths_to_process and not folder_to_process:
        path = prompt_for_path()
        if not path:
            print('No path provided. Exiting.')
            return
        if os.path.isdir(path):
            folder_to_process = path
        else:
            paths_to_process = [path]

    # Process paths
    processed_files = 0
    processed_folders = 0

    # Handle paths passed as arguments (including Drag and Drop)
    if paths_to_process:
        for path in paths_to_process:
            if not os.path.exists(path):
                print(f'Skip: {path} (does not exist)')
                continue
            if os.path.isdir(path):
                count = process_folder(path, optimize=optimize, svgz=svgz_output, vec=vec_output)
                if count > 0:
                    processed_folders += 1
                    print(f'Processed {count} SVGs in folder {path}')
                else:
                    print(f'No SVG files found in folder {path}')
            elif os.path.isfile(path) and path.lower().endswith(('.svg', '.svgz')):
                output_base = os.path.splitext(path)[0]
                if process_svg(path, output_base, optimize=optimize, svgz=svgz_output, vec=vec_output):
                    processed_files += 1
            else:
                print(f'Skip: {path} (not an SVG file)')

    # Handle folder specified via --folder
    if folder_to_process:
        if not os.path.isdir(folder_to_process):
            print(f'Error: {folder_to_process} is not a folder or does not exist')
        else:
            count = process_folder(folder_to_process, optimize=optimize, svgz=svgz_output, vec=vec_output)
            if count > 0:
                processed_folders += 1
                print(f'Processed {count} SVGs in folder {folder_to_process}')
            else:
                print(f'No SVG files found in folder {folder_to_process}')

    # Final message
    if processed_files > 0 or processed_folders > 0:
        print(f'\nTotal: {processed_files} files and {processed_folders} folders processed')
    else:
        print('\nNothing processed')

if __name__ == '__main__':
    main()