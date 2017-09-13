import run

if __name__ == '__main__':
    try:
        import settings_local as settings
        print("Imported local settings.")
    except ImportError:
        import settings
        print("Imported default settings.")

    run.run(settings)
