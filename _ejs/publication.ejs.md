```{=html}
<div class="pub-listing list">
<div class="listing-no-matching d-none">
No matching items
</div>

<% for (const item of items) { %>
<div class="quarto-post pub-entry" <%= metadataAttrs(item) %>>
  <div class="pub-body">
    <h3 class="no-anchor listing-title pub-title"><%= item.title %></h3>
    <div class="listing-author pub-authors"><%= item.author %></div>
    <div class="pub-venue">
      <em><%= item.journal %></em><% if (item.volume && item.volume !== 'n/a') { %>, <%= item.volume %><% } %><% if (item.number && item.number !== 'n/a') { %> (<%= item.number %>)<% } %>
      (<span class="listing-date"><%= item.year %></span>)
    </div>

    <% if (item.description) { %>
    <details class="pub-abstract">
      <summary>Abstract</summary>
      <p class="listing-description"><%= item.description %></p>
    </details>
    <% } %>

    <div class="pub-links">
      <% if (item.doi_url) { %>
        <a href="<%- item.doi_url %>" class="pub-btn" target="_blank" rel="noopener">
          <i class="bi bi-journal-text"></i> Paper
        </a>
      <% } %>
      <% if (item.preprint_url) { %>
        <a href="<%- item.preprint_url %>" class="pub-btn" target="_blank" rel="noopener">
          <i class="bi bi-file-earmark-text"></i> Preprint
        </a>
      <% } %>
      <% if (item.code_url) { %>
        <a href="<%- item.code_url %>" class="pub-btn" target="_blank" rel="noopener">
          <i class="bi bi-code-slash"></i> Code
        </a>
      <% } %>
      <% if (item.data_url) { %>
        <a href="<%- item.data_url %>" class="pub-btn" target="_blank" rel="noopener">
          <i class="bi bi-database"></i> Data
        </a>
      <% } %>
      <% if (item.osf_url) { %>
        <a href="<%- item.osf_url %>" class="pub-btn" target="_blank" rel="noopener">
          <i class="bi bi-box-arrow-up-right"></i> OSF
        </a>
      <% } %>
      <% if (item.github_url) { %>
        <a href="<%- item.github_url %>" class="pub-btn" target="_blank" rel="noopener">
          <i class="bi bi-github"></i> GitHub
        </a>
      <% } %>
      <% if (item.pdf_url) { %>
        <a href="<%- item.pdf_url %>" class="pub-btn" target="_blank" rel="noopener">
          <i class="bi bi-file-pdf"></i> PDF
        </a>
      <% } %>
      <% if (item.bibtex) { %>
        <button class="pub-btn pub-btn-cite" onclick="this.parentElement.nextElementSibling.classList.toggle('d-none')" aria-label="Show BibTeX citation">
          <i class="bi bi-quote"></i> Cite
        </button>
      <% } %>
    </div>

    <% if (item.bibtex) { %>
    <div class="pub-bibtex d-none">
      <div class="pub-bibtex-header">
        <span>BibTeX</span>
        <button class="pub-btn-copy" onclick="navigator.clipboard.writeText(this.parentElement.nextElementSibling.textContent.trim());this.textContent='Copied!';setTimeout(()=>this.textContent='Copy',1500)" aria-label="Copy BibTeX to clipboard">Copy</button>
      </div>
      <pre class="pub-bibtex-code"><%= item.bibtex %></pre>
    </div>
    <% } %>

    <% if (item.categories) { %>
    <div class="listing-categories">
      <% for (const cat of item.categories) { %>
        <span class="listing-category"><%= cat %></span>
      <% } %>
    </div>
    <% } %>
  </div>
</div>
<% } %>

</div>
```
