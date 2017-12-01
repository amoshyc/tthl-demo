import sass

if __name__ == '__main__':
    res = sass.compile(filename='static/style.scss', output_style='compressed')
    with open('static/style.css', 'w') as f:
        f.write(res)