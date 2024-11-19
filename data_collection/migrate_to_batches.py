import json
import save

if __name__ == "__main__":

    progress_json = {}
    with open(f"{save.STORAGE_REPOSITORY}\\progress.json", "r", encoding="utf-8") as f:
        progress_json = json.load(f)

    print(len(progress_json))

    commanders_list = list(progress_json.keys())
    urlhashes_list = list(progress_json.values())

    for i in range(0, len(progress_json), save.BATCH_SIZE):
        number = int(round(i / save.BATCH_SIZE))

        max_bound = (i + save.BATCH_SIZE) if i + save.BATCH_SIZE < len(progress_json) else len(progress_json)
        commanders_span = commanders_list[i:max_bound]
        urlhashes_span = urlhashes_list[i:max_bound]

        # update index
        
        with open(f"{save.STORAGE_REPOSITORY}{save.SAVE_INFO_REPOSITORY}{save.HISTORY_INDEX_FILE}", "a", encoding="utf-8") as f:
            f.write("@".join(commanders_span) + "\n")

        with open(f"{save.STORAGE_REPOSITORY}{save.SAVE_INFO_REPOSITORY}{save.HISTORY_FILE_PREF}{number}{save.HISTORY_FILE_EXT}", "w", encoding="utf-8") as f:
            json.dump({commander: urlhash_list for commander, urlhash_list in zip(commanders_span, urlhashes_span)}, f, indent="\t")