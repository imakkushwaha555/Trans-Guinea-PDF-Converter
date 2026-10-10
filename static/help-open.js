(() => {
    const target = location.hash && document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (target && target.tagName === "DETAILS") {
        target.open = true;
        target.scrollIntoView();
    }
})();
