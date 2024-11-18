from flask import Flask, render_template

@app.route('/kintai/input')
def input():
    return render_template('kintai-input.html')

@app.route('/kintai/search')
def search():
    return render_template('kintai-search.html')
