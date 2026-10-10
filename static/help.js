(() => {
    const form = document.getElementById("helpSearch");
    if (!form) return;
    const input = form.querySelector("input");
    const results = document.getElementById("helpResults");
    let timer;

    const render = (items, query) => {
        results.replaceChildren();
        if (!query) return;
        if (!items.length) {
            const p = document.createElement("p");
            p.className = "help-empty";
            p.textContent = "No matching help articles. Try another word, or open Help & support.";
            results.append(p);
            return;
        }
        for (const item of items) {
            const article = document.createElement("a");
            article.className = "help-result";
            article.href = "/help#" + item.id;
            const title = document.createElement("strong");
            title.textContent = item.title;
            const body = document.createElement("span");
            body.textContent = item.body;
            article.append(title, body);
            results.append(article);
        }
    };

    const run = async () => {
        const query = input.value.trim();
        if (!query) return render([], "");
        try {
            const response = await fetch("/help/search?q=" + encodeURIComponent(query));
            render(response.ok ? await response.json() : [], query);
        } catch {
            render([], query);
        }
    };

    input.addEventListener("input", () => {
        clearTimeout(timer);
        timer = setTimeout(run, 150);
    });
    form.addEventListener("submit", (event) => {
        event.preventDefault();
        run();
    });
})();
