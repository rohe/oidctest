<!DOCTYPE html>

<html>
<head>
    <title>Test tool instance</title>
    <style>
        .button {
            background-color: #4CAF50; /* Green */
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
        }
    </style>
</head>
<body>
<h1>What do you want to do with this test tool instance?</h1>
<form action="${qargs[-1]}/action" method="get">
    <table>
        <tr>
            <td>
                <button type="submit" value="delete" class="button">delete</button>
            </td>
        </tr>
        <tr>
            <td>
                <button type="submit" value="restart" class="button">restart</button>
            </td>
        </tr>
        <tr>
            <td>
                <button type="submit" value="configure" class="button">configure</button>
            </td>
        </tr>
    </table>
</form>
</body>
</html>