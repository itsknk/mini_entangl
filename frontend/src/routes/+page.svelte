<script lang="ts">
  import {
    analyzeMarkdown,
    fixMarkdown,
    type AnalyzeResponse,
    type FixResponse
  } from '$lib/api';

  /* ---------- state ---------- */
  let markdown = `1. Shut down mains
2. Kill main feed
3. Start backup generator`;

  let result: AnalyzeResponse | null = null;
  let fixResult: FixResponse | null = null;

  let loading = false;
  let error: string | null = null;

  /* ---------- helpers ---------- */
  const issueFor = (step: number) => result?.issues.find((i) => i.step_number === step);

  async function runAnalysis() {
    loading = true;
    error = null;
    try {
      result = await analyzeMarkdown(markdown);
    } catch (err: any) {
      error = err?.message ?? 'Unknown error';
    } finally {
      loading = false;
    }
  }

  async function runFix() {
    loading = true;
    error = null;
    try {
      fixResult = await fixMarkdown(markdown);
      markdown = fixResult.fixed_markdown;
      await runAnalysis();                    // show “No issues” state after fix
    } catch (err: any) {
      error = err?.message ?? 'Unknown error';
    } finally {
      loading = false;
    }
  }

  function copyFixed() {
    navigator.clipboard.writeText(fixResult!.fixed_markdown);
  }
</script>

<div class="card">
  <h1>Mini‑Entangl Demo</h1>

  <textarea bind:value={markdown} rows="8" />

  <div class="btn-row">
    <button class="primary" on:click={runAnalysis} disabled={loading}>
      {#if loading}
        Analyzing…
      {:else if result}
        {result.issues.length
          ? `${result.issues.length} issue${result.issues.length === 1 ? '' : 's'} found`
          : 'Re‑analyze'}
      {:else}
        Analyze
      {/if}
    </button>

    <button
      class="success"
      on:click={runFix}
      disabled={loading || !result || !result.issues.length}
    >
      {loading ? 'Fixing…' : 'Apply Suggested Fixes'}
    </button>
  </div>

  {#if error}
    <p class="error">{error}</p>
  {/if}

  {#if result}
    <h2>Steps</h2>
    <ol>
      {#each result.steps as step}
        <li class={issueFor(step.number) ? 'bad' : 'ok'}>
          {#if issueFor(step.number)}
            <!-- red warning icon -->
            <svg class="icon red" viewBox="0 0 16 16">
              <path d="M8 1.333 1.333 14h13.334L8 1.333Zm-.667 4h1.334v4H7.333V5.333Zm0 5.334h1.334v1.333H7.333v-1.333Z"/>
            </svg>
          {:else}
            <!-- green check icon -->
            <svg class="icon green" viewBox="0 0 16 16">
              <path d="M6.667 10.28 4 7.613l-.94.94 3.607 3.607 6.273-6.273-.94-.94-5.333 5.333Z"/>
            </svg>
          {/if}
          {step.raw}
        </li>
      {/each}
    </ol>

    {#if result.issues.length}
      <h2>Issues</h2>
      <ul>
        {#each result.issues as i}
          <li>
            <strong>Step {i.step_number}:</strong> {i.description}<br />
            <em>Suggestion:</em> {i.suggestion}
          </li>
        {/each}
      </ul>
    {:else}
      <p class="no-issues">✅ No issues detected!</p>
    {/if}
  {/if}

  {#if fixResult}
    <h2>Corrected Steps</h2>
    <textarea rows="6" readonly bind:value={fixResult.fixed_markdown} />
    <button class="primary" on:click={copyFixed}>Copy corrected steps</button>
  {/if}
</div>

<!-- Google Font -->
<link rel="preconnect" href="https://fonts.gstatic.com" />
<link
  href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap"
  rel="stylesheet"
/>

<style>
  /* ====== Global / layout ====== */
  :global(body) {
    margin: 0;
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    background: #f4f6f8;
  }
  .card {
    max-width: 720px;
    margin: 32px auto;
    padding: 24px 32px 40px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.08);
  }
  h1 {
    margin: 0 0 12px;
    color: #334155;
  }
  h2 {
    margin: 24px 0 8px;
    color: #475569;
  }

  /* ====== Inputs ====== */
  textarea {
    width: 100%;
    font-family: monospace;
    font-size: 15px;
    padding: 10px;
    margin-bottom: 12px;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    background: #f8fafc;
    box-sizing: border-box;
  }
  textarea[readonly] {
    background: #f1f5f9;
    color: #334155;
  }

  /* ====== Buttons ====== */
  .btn-row {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
  }
  button {
    padding: 8px 18px;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s;
  }
  .primary {
    background: #e2e8f0;
    color: #0f172a;
  }
  .primary:hover:not([disabled]) {
    background: #cbd5e1;
  }
  .success {
    background: #16a34a;
    color: #fff;
  }
  .success:hover:not([disabled]) {
    background: #15803d;
  }
  button[disabled] {
    opacity: 0.45;
    cursor: default;
  }

  /* ====== Step list ====== */
  ol {
    padding-left: 28px;
  }
  li {
    margin: 4px 0;
    display: flex;
    align-items: flex-start;
    gap: 6px;
  }
  .icon {
    width: 18px;
    height: 18px;
    flex: 0 0 18px;
  }
  .icon.red {
    color: #dc2626;
  }
  .icon.green {
    color: #16a34a;
  }
  .bad {
    color: #dc2626;
  }
  .ok {
    color: #16a34a;
  }

  /* ====== Status & errors ====== */
  .error {
    color: #dc2626;
    font-weight: 600;
  }
  .no-issues {
    font-weight: 600;
    color: #16a34a;
    margin: 4px 0;
  }

  /* ====== Responsive tweak ====== */
  @media (max-width: 640px) {
    .card {
      margin: 12px 8px;
      padding: 20px;
    }
    textarea {
      font-size: 14px;
    }
    h1 {
      font-size: 1.4rem;
    }
  }
</style>
