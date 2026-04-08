import sys
from pathlib import Path

from bokeh.util.compiler import nodejs_compile

# Ensure we are in the project root
PROJECT_ROOT = Path(__file__).parent.absolute()
TS_SRC_DIR = PROJECT_ROOT / "ts" / "src"
JS_OUT_DIR = PROJECT_ROOT / "src" / "bokeh_customizations" / "js"


def compile_ts_files():
    if not JS_OUT_DIR.exists():
        JS_OUT_DIR.mkdir(parents=True)

    ts_files = list(TS_SRC_DIR.glob("*.ts"))
    if not ts_files:
        print("No .ts files found in ts/src/")
        return

    print(f"Compiling {len(ts_files)} files...")

    for ts_file in ts_files:
        js_file = JS_OUT_DIR / (ts_file.stem + ".js")
        print(f"  {ts_file.name} -> {js_file.name}")

        with open(ts_file, "r") as f:
            code = f.read()

        try:
            # We use nodejs_compile to get the raw CommonJS output.
            # This is exactly what Bokeh would do internally.
            compiled = nodejs_compile(code, lang="typescript", file=str(ts_file))

            # The 'code' in the result is the transpiled JS.
            with open(js_file, "w") as f:
                f.write(compiled.code)

            # Optionally write source maps if available
            if "map" in compiled and compiled.map:
                with open(str(js_file) + ".map", "w") as f:
                    f.write(compiled.map)

        except Exception as e:
            print(f"Error compiling {ts_file.name}: {e}")
            if "node.js" in str(e).lower():
                print("\nFATAL: Node.js is required for building JS files.")
                print("Please ensure node is in your PATH.")
            sys.exit(1)

    print("Done!")


if __name__ == "__main__":
    compile_ts_files()
