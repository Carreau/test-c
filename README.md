# SQLite Database Research Tool

A simple HTML/JavaScript tool for querying SQLite databases directly in the browser or via Cloudflare Workers.

## Static Web Page (sql.js)

### Features
- Load SQLite databases from URLs
- Execute SQL queries directly in the browser
- View database schema
- No backend required - runs entirely client-side
- Clean, responsive UI

### Usage

1. **Open the HTML file**: Open `sqlite-research.html` in a web browser

2. **Load a database**:
   - Enter the URL of your SQLite database file
   - Click "Load Database"
   - The database will be downloaded and loaded into memory

3. **Execute queries**:
   - Enter your SQL query in the text area
   - Click "Execute Query"
   - Results will be displayed in a table below

4. **View schema**:
   - Click "Show Schema" to see all tables, views, and indexes

### Testing with the Sample Database

This repository includes a sample database (`sample.db`) with business data for testing:

**Tables:**
- `employees` - 10 employees with departments, salaries, and hire dates
- `products` - 10 products with categories, prices, and stock levels
- `orders` - 8 sample orders linked to employees
- `order_items` - 14 order line items

**To test locally:**
1. Open `sqlite-research.html` in a browser
2. Use the file path: `file:///path/to/sample.db` or serve it via a local web server
3. See `SAMPLE_QUERIES.md` for example queries to try

**To test via HTTP:**
Host the `sample.db` file on a static server and use the full URL.

### Other Example Databases

You can also test with publicly available SQLite databases:
- Chinook Database: `https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite`
- Or host your own database file on any static file server

### Limitations
- The entire database is loaded into browser memory
- Large databases may be slow or fail to load
- Read-only (no writes persist)

---

## Cloudflare Worker Alternative

For better performance with large databases or when you need server-side processing, you can use a Cloudflare Worker with D1 (Cloudflare's SQLite database).

### Setup

1. **Install Wrangler CLI**:
```bash
npm install -g wrangler
```

2. **Create a new Worker project**:
```bash
mkdir sqlite-worker
cd sqlite-worker
npm init -y
npm install wrangler --save-dev
```

3. **Create Worker script** (`worker.js`):

```javascript
export default {
  async fetch(request, env) {
    // Handle CORS
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }

    const url = new URL(request.url);

    // Health check endpoint
    if (url.pathname === '/') {
      return new Response('SQLite Research API is running', {
        headers: { 'Access-Control-Allow-Origin': '*' },
      });
    }

    // Query endpoint
    if (url.pathname === '/query' && request.method === 'POST') {
      try {
        const { sql } = await request.json();

        if (!sql) {
          return new Response(JSON.stringify({ error: 'SQL query is required' }), {
            status: 400,
            headers: {
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': '*',
            },
          });
        }

        // Execute query on D1 database
        const { results } = await env.DB.prepare(sql).all();

        return new Response(JSON.stringify({ results }), {
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          },
        });
      } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          },
        });
      }
    }

    // Schema endpoint
    if (url.pathname === '/schema' && request.method === 'GET') {
      try {
        const { results } = await env.DB.prepare(
          "SELECT type, name, sql FROM sqlite_master WHERE sql NOT NULL ORDER BY type, name"
        ).all();

        return new Response(JSON.stringify({ results }), {
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          },
        });
      } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          },
        });
      }
    }

    return new Response('Not Found', { status: 404 });
  },
};
```

4. **Create `wrangler.toml`**:

```toml
name = "sqlite-research-worker"
main = "worker.js"
compatibility_date = "2024-01-01"

[[d1_databases]]
binding = "DB"
database_name = "your-database-name"
database_id = "your-database-id"
```

5. **Create D1 Database**:
```bash
wrangler d1 create your-database-name
```

This will output a database ID - add it to your `wrangler.toml`.

6. **Import data** (optional):
```bash
wrangler d1 execute your-database-name --file=./schema.sql
```

7. **Deploy**:
```bash
wrangler deploy
```

### Frontend for Cloudflare Worker

Create an HTML file that connects to your Worker:

```html
<!DOCTYPE html>
<html>
<head>
    <title>SQLite Research - Cloudflare Worker</title>
</head>
<body>
    <h1>SQLite Research Tool</h1>
    <textarea id="query" placeholder="Enter SQL query"></textarea>
    <button onclick="executeQuery()">Execute</button>
    <div id="results"></div>

    <script>
        const WORKER_URL = 'https://your-worker.your-subdomain.workers.dev';

        async function executeQuery() {
            const query = document.getElementById('query').value;

            try {
                const response = await fetch(`${WORKER_URL}/query`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sql: query })
                });

                const data = await response.json();

                if (data.error) {
                    document.getElementById('results').innerHTML =
                        `<p style="color: red;">Error: ${data.error}</p>`;
                } else {
                    displayResults(data.results);
                }
            } catch (error) {
                document.getElementById('results').innerHTML =
                    `<p style="color: red;">Error: ${error.message}</p>`;
            }
        }

        function displayResults(results) {
            if (!results || results.length === 0) {
                document.getElementById('results').innerHTML = '<p>No results</p>';
                return;
            }

            const keys = Object.keys(results[0]);
            let html = '<table border="1"><tr>';

            keys.forEach(key => html += `<th>${key}</th>`);
            html += '</tr>';

            results.forEach(row => {
                html += '<tr>';
                keys.forEach(key => html += `<td>${row[key]}</td>`);
                html += '</tr>';
            });

            html += '</table>';
            document.getElementById('results').innerHTML = html;
        }
    </script>
</body>
</html>
```

## Comparison

| Feature | Static Page (sql.js) | Cloudflare Worker |
|---------|---------------------|-------------------|
| Setup Complexity | Very simple | Moderate |
| Database Size | Limited by browser memory | Up to 10GB (D1) |
| Performance | Client-side processing | Server-side processing |
| Cost | Free | Free tier available |
| Persistence | Read-only | Read/Write supported |
| Hosting | Any static host | Cloudflare |

## Security Notes

- For production use, implement proper authentication
- Sanitize SQL queries to prevent injection attacks
- Consider rate limiting for public endpoints
- Never expose sensitive data without proper access controls

## License

MIT
