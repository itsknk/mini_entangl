<script lang="ts">
  import { analyzeMarkdown, fixMarkdown, type AnalyzeResponse, type FixResponse } from '$lib/api';

  let markdown = `1. Shut down mains
2. Start backup generator
3. Perform maintenance`;

  let result: AnalyzeResponse | null = null;
  let loading = false;
  let error: string | null = null;

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

  let fixResult: FixResponse | null = null;

  async function runFix() {
    loading = true;
    try {
      fixResult = await fixMarkdown(markdown);
      markdown = fixResult.fixed_markdown;   // replace textarea contents
      await runAnalysis();                   // re-run to show “no issues”
    } catch (err: any) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

</script>

<h1>Mini-Entangl Demo</h1>

<textarea bind:value={markdown} rows="8" style="width:100%;"></textarea>
<br />
<button on:click={runAnalysis} disabled={loading}>
  {loading ? 'Analyzing…' : 'Analyze'}
</button>
<button on:click={runFix} disabled={loading || !result || result.issues.length === 0}>
  {loading ? 'Fixing…' : 'Apply Suggested Fixes'}
</button>

{#if error}
  <p style="color:red;">{error}</p>
{/if}

{#if result}
  <h2>Steps</h2>
  <ol>
    {#each result.steps as step}
      <li>
        {step.raw}
        {#if result.issues.find(i => i.step_number === step.number)}
          <strong style="color:red;"> ⚠ Needs reorder</strong>
        {/if}
      </li>
    {/each}
  </ol>

  {#if result.issues.length > 0}
    <h2>Issues</h2>
    <ul>
      {#each result.issues as issue}
        <li>
          Step {issue.step_number}: {issue.description}<br />
          <em>Suggestion:</em> {issue.suggestion}
        </li>
      {/each}
    </ul>
  {:else}
    <p>No issues detected!</p>
  {/if}
{/if}
