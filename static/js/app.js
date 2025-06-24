document.addEventListener('DOMContentLoaded', function() {
    const loadBtn = document.getElementById('load-articles');
    const articlesDiv = document.getElementById('articles');

    loadBtn.addEventListener('click', async function() {
        articlesDiv.innerHTML = '<p>Loading articles...</p>';
        try {
            const res = await fetch('/api/proptech-intelligence');
            const data = await res.json();
            if (data.intelligence && data.intelligence.length > 0) {
                articlesDiv.innerHTML = data.intelligence.map(article => {
                    const articleUrl = article.url || article.link || '';
                    // Parse AI summary into table with bold headers
                    let summaryRows = '';
                    let summaryBlocks = '';
                    if (article.summary || article.proptech_analysis) {
                        const analysisText = article.summary || article.proptech_analysis;
                        const sections = analysisText.split('**');
                        if (sections.length > 1) {
                            // Table rows for desktop
                            summaryRows = sections.slice(1).reduce((acc, val, idx, arr) => {
                                if (idx % 2 === 0 && arr[idx + 1]) {
                                    const label = arr[idx].replace(':', '').trim();
                                    const content = arr[idx + 1].trim();
                                    if (content && !content.startsWith('[')) {
                                        acc += `<tr><td class='font-semibold text-gray-700 bg-gray-100 px-3 py-2 w-1/3'>${label}</td><td class='text-gray-800 px-3 py-2'>${content}</td></tr>`;
                                    }
                                }
                                return acc;
                            }, '');
                            // Blocks for mobile
                            summaryBlocks = sections.slice(1).reduce((acc, val, idx, arr) => {
                                if (idx % 2 === 0 && arr[idx + 1]) {
                                    const label = arr[idx].replace(':', '').trim();
                                    const content = arr[idx + 1].trim();
                                    if (content && !content.startsWith('[')) {
                                        acc += `<div class='mb-2'><span class='font-semibold text-gray-700'>${label}:</span> <span class='text-gray-800'>${content}</span></div>`;
                                    }
                                }
                                return acc;
                            }, '');
                        } else {
                            // Fallback for old format
                            const points = analysisText.split(/\n?\s*\d+\.\s+/).filter(Boolean);
                            summaryRows = points.map((point, idx) => {
                                const colonIdx = point.indexOf(':');
                                let label = `Point ${idx + 1}`;
                                let content = point;
                                if (colonIdx > 0) {
                                    label = point.slice(0, colonIdx).trim();
                                    content = point.slice(colonIdx + 1).trim();
                                }
                                return `<tr><td class='font-semibold text-gray-700 bg-gray-100 px-3 py-2 w-1/3'>${label}</td><td class='text-gray-800 px-3 py-2'>${content}</td></tr>`;
                            }).join('');
                            summaryBlocks = points.map((point, idx) => {
                                const colonIdx = point.indexOf(':');
                                let label = `Point ${idx + 1}`;
                                let content = point;
                                if (colonIdx > 0) {
                                    label = point.slice(0, colonIdx).trim();
                                    content = point.slice(colonIdx + 1).trim();
                                }
                                return `<div class='mb-2'><span class='font-semibold text-gray-700'>${label}:</span> <span class='text-gray-800'>${content}</span></div>`;
                            }).join('');
                        }
                    } else {
                        summaryRows = '';
                        summaryBlocks = '<div class="text-gray-500 italic">No summary available.</div>';
                    }
                    return `
  <div class="bg-white rounded-xl shadow p-6 flex flex-col gap-4">
    <div class="flex flex-row items-start justify-between gap-4 mb-2">
      <h2 class="text-lg font-bold text-gray-900 break-words flex-1 pr-2">${article.title}</h2>
      ${articleUrl ? `<a href="${articleUrl}" target="_blank" rel="noopener noreferrer">
        <button class="bg-[oklch(69.6%_0.17_162.48)] text-white font-semibold py-2 px-4 rounded-lg transition text-base whitespace-nowrap" style="--tw-bg-opacity:1;" onmouseover="this.style.background='oklch(39.3% 0.095 152.535)'" onmouseout="this.style.background='oklch(69.6% 0.17 162.48)'">
          Read More
        </button>
      </a>` : ''}
    </div>
    <div class="flex flex-col sm:flex-row sm:items-center text-sm text-gray-500 gap-1">
      <span>Source: ${article.source || ''}</span>
      ${article.published ? `<span class="hidden sm:inline mx-2">|</span><span>Date: ${article.published}</span>` : ''}
      ${article.author ? `<span class="hidden sm:inline mx-2">|</span><span>Author: ${article.author}</span>` : ''}
    </div>
    <div>
      <div class="font-semibold text-gray-700 mb-1">AI Summary:</div>
      <div class="overflow-x-auto">
        <table class="min-w-full text-sm bg-gray-50 rounded-lg overflow-hidden my-2 hidden sm:table">
          <tbody>
            ${summaryRows}
          </tbody>
        </table>
        <div class="sm:hidden flex flex-col gap-2">
          ${summaryBlocks}
        </div>
      </div>
    </div>
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