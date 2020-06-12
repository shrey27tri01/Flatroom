if (localStorage.getItem('last_channel')) {
    let channel = localStorage.getItem('last_channel');    
    window.location.replace('/channels/' + channel);   
}

document.querySelector('#change-avatar').onclick = () => {
    document.querySelector('#pic').innerHTML = `<img src="https://icotar.com/avatar/${Math.random().toString(36).slice(2)}.png?size=200">`;
    console.log(document.querySelector('#pic').innerHTML);
};