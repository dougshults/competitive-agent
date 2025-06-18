document.addEventListener('DOMContentLoaded', function() {
    const loadBtn = document.getElementById('load-articles');
    const articlesDiv = document.getElementById('articles');

    loadBtn.addEventListener('click', async function() {
        articlesDiv.innerHTML = '<p>Loading articles...</p>';
        try {
            const res = await fetch('/api/proptech-articles');
            const data = await res.json();
            if (data.articles && data.articles.length > 0) {
                articlesDiv.innerHTML = data.articles.map(article => {
                    const articleUrl = article.url || article.link;
                    return `
                        <div class="article">
                            <div class="article-title">${article.title}</div>
                            ${articleUrl ? `<a class="article-link" href="${articleUrl}" target="_blank" rel="noopener noreferrer">Read more</a>` : ''}
                            <div class="article-source">Source: ${article.source || ''}</div>
                        </div>
                    `;
                }).join('');
            } else {
                articlesDiv.innerHTML = '<p>No articles found.</p>';
            }
        } catch (err) {
            articlesDiv.innerHTML = '<p>Error loading articles.</p>';
        }
    });
}); 