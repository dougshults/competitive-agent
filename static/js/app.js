document.addEventListener('DOMContentLoaded', function() {
    const loadBtn = document.getElementById('load-articles');
    const articlesDiv = document.getElementById('articles');

    loadBtn.addEventListener('click', async function() {
        articlesDiv.innerHTML = '<p>Loading articles...</p>';
        try {
            const res = await fetch('/api/proptech-intelligence');
            const data = await res.json();
            if (data.analyses && data.analyses.length > 0) {
                articlesDiv.innerHTML = data.analyses.map(article => {
                    const articleUrl = article.link || '';
                    // Parse AI summary into table with bold headers
                    let summaryTable = '';
                    if (article.proptech_analysis) {
                        // Split summary by bold headers (**LABEL:**)
                        const sections = article.proptech_analysis.split('**');
                        if (sections.length > 1) {
                            summaryTable = `<table class="ai-summary-table"><tbody>`;
                            for (let i = 1; i < sections.length; i += 2) {
                                if (i + 1 < sections.length) {
                                    const label = sections[i].replace(':', '').trim();
                                    const content = sections[i + 1].trim();
                                    if (content && !content.startsWith('[')) {
                                        summaryTable += `<tr><td class="ai-summary-label">${label}</td><td class="ai-summary-content">${content}</td></tr>`;
                                    }
                                }
                            }
                            summaryTable += `</tbody></table>`;
                        } else {
                            // Fallback to old numbered format if no bold headers found
                            const points = article.proptech_analysis.split(/\n?\s*\d+\.\s+/).filter(Boolean);
                            summaryTable = `<table class="ai-summary-table"><tbody>`;
                            points.forEach((point, idx) => {
                                const colonIdx = point.indexOf(':');
                                let label = `Point ${idx + 1}`;
                                let content = point;
                                if (colonIdx > 0) {
                                    label = point.slice(0, colonIdx).trim();
                                    content = point.slice(colonIdx + 1).trim();
                                }
                                summaryTable += `<tr><td class="ai-summary-label">${label}</td><td class="ai-summary-content">${content}</td></tr>`;
                            });
                            summaryTable += `</tbody></table>`;
                        }
                    } else {
                        summaryTable = '<div class="article-summary">No summary available.</div>';
                    }
                    return `
                        <div class="article">
                            <div class="article-title">${article.title}</div>
                            ${articleUrl ? `<a class="article-link" href="${articleUrl}" target="_blank" rel="noopener noreferrer">Read more</a>` : ''}
                            <div class="article-source">Source: ${article.source || ''}</div>
                            <div class="article-summary"><strong>AI Summary:</strong>${summaryTable}</div>
                        </div>
                    `;
                }).join('');
            } else {
                articlesDiv.innerHTML = '<p>No articles found.</p>';
            }
        } catch (err) {
            articlesDiv.innerHTML = '<p>Error loading articles.</p>';
            console.error('Error:', err);
        }
    });
}); 