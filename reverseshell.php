<?php
    $uploaded_file = $_FILES['uploaded_file'];
    move_uploaded_file($uploaded_file['tmp_name'], 'uploads/' . $uploaded_file['name']);
?>